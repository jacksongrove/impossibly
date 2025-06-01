'''
Defines individual agent types to be called within the graph structure.

Author: Jackson Grove
'''
import os, shutil, textwrap, base64, asyncio, inspect
from typing import Union, List
from openai import AsyncOpenAI, OpenAI
from openai import File
from anthropic import AsyncAnthropic, Anthropic
from impossibly.utils.start_end import END
from impossibly.utils.memory import Memory
from impossibly.utils.tools import Tool, format_tools_for_api

#TODO: Add shared memory to agent (list of agents to read memory from)
#TODO: Add tool use

class Agent:
    '''
    A unified agent that interfaces with a specific language model client.

    This class acts as a wrapper that abstracts away the details of the underlying API,
    dynamically delegating requests to either an OpenAI- or Anthropic-based agent. It sets
    up configuration parameters such as the model identifier, system prompt, agent name, and 
    an optional description used for initialization or runtime behavior.

    Parameters:
        client: An instance of either the OpenAI or Anthropic client. This determines
                which underlying agent (OpenAIAgent or AnthropicAgent) will be instantiated.
        model (str, optional): The identifier of the language model to be used. Defaults to "gpt-4o".
        name (str, optional): The name assigned to this agent. Defaults to "agent".
        system_prompt (str, optional): The system prompt that configures the agent's initial behavior.
                                       Defaults to "You are a helpful assistant.".
        description (str, optional): An additional description for the agent. Defaults to an empty string.
        shared_memory (list, optional): A list of agents to read memory from. Defaults to an empty list.
        tools (list[Tool], optional): A list of Tool instances that the agent can use. Defaults to an empty list.

    Attributes:
        client: The underlying agent instance (either OpenAIAgent or AnthropicAgent).
        model (str): The identifier of the language model.
        name (str): The name of the agent.
        system_prompt (str): The system prompt configuring the agent's behavior.
        description (str): An additional description for the agent.
        shared_memory (list of Agents): A list of agents to read memory from.
        tools (list[Tool]): A list of tools available to the agent.

    Raises:
        ValueError: If the provided client is not an instance of either OpenAI or Anthropic.
    '''

    def __init__(self, client, model: str = "gpt-4o", name: str = "agent", system_prompt: str = "You are a helpful assistant.", description: str = "", files: List[str] = [], shared_memory: List['Agent'] = None, tools: List[Tool] = []) -> None:
        if isinstance(client, (AsyncOpenAI, OpenAI)):
            self.client = OpenAIAgent(client, system_prompt, model, name, description, routing_instructions="", files=files, tools=tools)
        elif isinstance(client, (AsyncAnthropic, Anthropic)):
            self.client = AnthropicAgent(client, system_prompt, model, name, description, tools) # Excluding 'files' since Anthropic doesn't support RAG
        else:
            raise ValueError("Client must be an instance of AsyncOpenAI, OpenAI, AsyncAnthropic, or Anthropic")
        self.model = self.client.model
        self.name = self.client.name
        self.system_prompt = self.client.system_prompt
        self.messages = self.client.messages
        self.description = self.client.description
        self.shared_memory = shared_memory
        
        # Set files attribute based on client type - Anthropic doesn't support RAG
        if isinstance(self.client, OpenAIAgent):
            self.files = self.client.files
        else:
            # For Anthropic, set to empty list
            self.files = []
            
        self.tools = tools

    def invoke(self, author: str, prompt: str, files: List[str] = [], edges: List['Agent'] = None, show_thinking: bool = False) -> str:
        '''
        Public method that transparently handles both sync and async execution.
        
        This method detects if it's being called from an async context and acts accordingly.
        If called from sync code, it runs the async implementation using asyncio.run().
        If called from async code, it returns a coroutine that can be awaited.
        
        This provides a unified API that works for both sync and async callers.
        
        Args:
            author (str): The author of the message ('user', 'system', 'assistant', etc.).
            prompt (str): The prompt to send to the agent.
            files (list[str], optional): A list of file paths to include. Defaults to [].
            edges (list[Agent], optional): A list of agents that this agent can route to. Defaults to None.
            show_thinking (bool, optional): Whether to show the agent's thinking process. Defaults to False.
            
        Returns:
            str: The agent's response.
        '''
        try:
            # Check if we're in an event loop
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # We're being called from an async context
                # Return the coroutine for the caller to await
                return self._invoke_async(author, prompt, files, edges, show_thinking)
            else:
                # No running event loop, create one
                return asyncio.run(self._invoke_async(author, prompt, files, edges, show_thinking))
        except RuntimeError:
            # No event loop exists, create one
            return asyncio.run(self._invoke_async(author, prompt, files, edges, show_thinking))

    async def _invoke_async(self, author: str, prompt: str, files: List[str] = [], edges: List['Agent'] = None, show_thinking: bool = False) -> str:
        '''
        Internal async implementation of invoke.
        
        Args:
            author (str): The author of the message ('user', 'system', 'assistant', etc.).
            prompt (str): The prompt to send to the agent.
            files (list[str], optional): A list of file paths to include. Defaults to [].
            edges (list[Agent], optional): A list of agents that this agent can route to. Defaults to None.
            show_thinking (bool, optional): Whether to show the agent's thinking process. Defaults to False.
            
        Returns:
            str: The agent's response.
        '''
        return await self.client.invoke(author, prompt, files, edges, show_thinking)


class OpenAIAgent:
    def __init__(self, client: Union[AsyncOpenAI, OpenAI], system_prompt: str, model: str = "gpt-4o", name: str = "agent", description: str = "A general purpose agent", routing_instructions: str = "", files: List[str] = [], tools: List[Tool] = []) -> None:
        self.client = client
        self.is_async = isinstance(client, AsyncOpenAI)
        self.model = model
        self.name = name
        self.system_prompt = system_prompt
        self.description = description
        self.routing_instructions = routing_instructions
        self.messages = [
            {"role": "system", "content": system_prompt}
        ]
        
        # Initialize RAG files differently depending on sync/async client
        if self.is_async:
            self.files = asyncio.run(self.init_rag_files_async(files)) if files else []
        else:
            self.files = self.init_rag_files_sync(files) if files else []
            
        self.tools = tools

    async def init_rag_files_async(self, files: List[str]) -> List['File']:
        '''
        Asynchronously initializes and uploads files for Retrieval-Augmented Generation (RAG) purposes.
        '''
        # Mapping of supported file extensions to their corresponding purpose
        supported_files = [".c", ".cs", ".cpp", ".doc", ".docx", ".html", ".java", ".json", ".md", ".pdf", ".php", ".pptx", ".py", ".rb", ".tex", ".txt", ".css", ".js", ".sh", ".ts", ".png", ".jpg", ".jpeg", ".gif", ".webp"]
        file_objects = []
        for path in files:
            if not path:
                continue
            ext = os.path.splitext(path)[1].lower()
            try:
                # Assert that the file extension is supported.
                assert ext in supported_files, (
                    f"Unsupported file type '{ext}'. Accepted types: {', '.join(supported_files)}"
                )
                # Create the file object using the appropriate purpose
                file_obj = await self.client.files.create(
                    file=open(path, "rb"),
                    purpose="assistants"
                )
                file_objects.append(file_obj)
            except AssertionError as ae:
                print(ae)
            except Exception as ex:
                print(f"Error processing {path}: {ex}")
                
        return file_objects
    
    def init_rag_files_sync(self, files: List[str]) -> List['File']:
        '''
        Synchronously initializes and uploads files for Retrieval-Augmented Generation (RAG) purposes.
        '''
        # Mapping of supported file extensions to their corresponding purpose
        supported_files = [".c", ".cs", ".cpp", ".doc", ".docx", ".html", ".java", ".json", ".md", ".pdf", ".php", ".pptx", ".py", ".rb", ".tex", ".txt", ".css", ".js", ".sh", ".ts", ".png", ".jpg", ".jpeg", ".gif", ".webp"]
        file_objects = []
        for path in files:
            if not path:
                continue
            ext = os.path.splitext(path)[1].lower()
            try:
                # Assert that the file extension is supported.
                assert ext in supported_files, (
                    f"Unsupported file type '{ext}'. Accepted types: {', '.join(supported_files)}"
                )
                # Create the file object using the appropriate purpose
                file_obj = self.client.files.create(
                    file=open(path, "rb"),
                    purpose="assistants"
                )
                file_objects.append(file_obj)
            except AssertionError as ae:
                print(ae)
            except Exception as ex:
                print(f"Error processing {path}: {ex}")
                
        return file_objects

    def init_input_files(self, files: List[str]) -> List['File']:
        '''
        Initializes and uploads input files for various purposes based on their type.

        This method processes a list of file paths, validates their extensions against a predefined mapping of supported file types to purposes (e.g., "assistants" or "vision"), and uploads them to 
        the OpenAI API. Uploaded files are returned as OpenAI File objects.

        Args:
            files (list[str]): A list of file paths to be uploaded, with their purpose determined by their extension.

        Returns:
            list[File]: A list of OpenAI File objects created by the OpenAI API.

        Raises:
            AssertionError: If a file's extension is not in the supported file types.
            Exception: If an error occurs during the file upload process.

        Notes:
            - Supported file types include text documents, images, and code files. For example:
                - Text/code files (e.g., `.txt`, `.py`, `.json`) are uploaded with the purpose "assistants".
                - Image files (e.g., `.png`, `.jpg`) are uploaded with the purpose "vision".
            - Unsupported files are skipped, and an error message is logged.
            - Ensure the provided file paths are valid and accessible.
        '''
        # Mapping of supported file extensions to their corresponding purpose
        supported_files = {
            ".c": "assistants",
            ".cs": "assistants",
            ".cpp": "assistants",
            ".doc": "assistants",
            ".docx": "assistants",
            ".html": "assistants",
            ".java": "assistants",
            ".json": "assistants",
            ".md": "assistants",
            ".pdf": "assistants",
            ".php": "assistants",
            ".pptx": "assistants",
            ".py": "assistants",
            ".rb": "assistants",
            ".tex": "assistants",
            ".txt": "assistants",
            ".css": "assistants",
            ".js": "assistants",
            ".sh": "assistants",
            ".ts": "assistants",
            ".png": "vision",
            ".jpg": "vision",
            ".jpeg": "vision",
            ".gif": "vision",
            ".webp": "vision",
        }
        # Prepare a string to display all accepted file types if needed
        accepted_types = ", ".join(sorted(supported_files.keys()))
        file_objects = []
        
        for path in files:
            if not path:
                continue
            ext = os.path.splitext(path)[1].lower()
            try:
                # Assert that the file extension is supported.
                assert ext in supported_files, (
                    f"Unsupported file type '{ext}'. Accepted types: {accepted_types}"
                )
                # Determine the purpose based on the file extension
                purpose = supported_files[ext]
                # Create the file object using the appropriate purpose
                file_obj = self.client.files.create(
                    file=open(path, "rb"),
                    purpose=purpose
                )
                file_objects.append(file_obj)
            except AssertionError as ae:
                print(ae)
            except Exception as ex:
                print(f"Error processing {path}: {ex}")
                
        return file_objects

    def _log_thinking(self, chat_prompt: str) -> None:
        '''
        Prints the intermediate outputs of the Agent in terminal, making thinking transparent throughout the execution of a Graph. All outputs are formatted to be clearly labelled when printed.

        Args:
            :chat_prompt (string): The prompt sent to the Agent.
        '''
        terminal_width = shutil.get_terminal_size((80, 20)).columns
        yellow = '\033[93m'
        green = '\033[92m'
        reset = '\033[0m'
        header = f" {green}{self.name}{reset} "
        visible_header = f" {header} "
        dashes = (terminal_width - len(visible_header)) // 2

        # Display agent name as header
        print(f"{yellow}{'-' * dashes}{reset}{visible_header}{yellow}{'-' * dashes}{reset}")
        
        # Helper function to enforce formatted prompts
        def format_text(text):
            formatted_lines = []
            for line in text.split("\n"):  # Preserve explicit newlines
                wrapped_lines = textwrap.wrap(line, width=terminal_width - 4)  # Wrap lines with adjusted width
                formatted_lines.extend(["    " + wrapped_line for wrapped_line in wrapped_lines])  # Add indentation
            return "\n".join(formatted_lines)

        # Display formatted prompts
        print(f"{yellow}System Prompt:{reset} {self.system_prompt}\n")
        print(f"{yellow}Chat Prompt:{reset}\n" + format_text(chat_prompt) + "\n")

    def _encode_image(self, image_path: str) -> str:
        '''
        Helper function to encode images in Base64 encoding. Used for image inputs.
        
        Args:
            image_path (str): Path to the image file
            
        Returns:
            str: Base64 encoded string of the image
        '''
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode("utf-8")
        except Exception as e:
            raise ValueError(f"Failed to encode image at {image_path}: {str(e)}")


    async def invoke(self, author: str, chat_prompt: str = "", files: List[str] = [], edges: List['Agent'] = None, show_thinking: bool = False) -> str:
        '''
        Prompts the model, returning a text response. System instructions, routing options and chat history are aggregated into the prompt in the following format:
            """
            ## System Instructions:
                {system_prompt}

            ## Chat Prompt:
                {chat_prompt}

            ## Optional Routing:
                You can route to the following agents: {edges}
                To route to a specific agent, include their name in the following format: \\AgentName\\
                Otherwise, I'll route to a random agent.
            """

        Args:
            chat_prompt (str): Content to prompt the chat model with
            edges (list[Agent]): Available agent routing options
            show_thinking (bool): Enables log printing of prompt and response from model

        Returns:
            str: The model's response to the prompt
        '''
        # Build the message prompt and history
        prompt = ""

        # Format the prompt with the chat prompt and routing instructions
        prompt += chat_prompt

        # Add routing information and cues if there are multiple potential routes the agent can take
        if edges and len(edges) > 1:
            # Make the routing information optional
            prompt += "\n\n--- Optional Routing ---\nYou can choose to route to one of the following agents:\n"
            
            # List all available agents with their descriptions
            for edge in edges:
                if edge != END:
                    prompt += f"- {edge.name}: {edge.description}\n"
                else:
                    prompt += f"- END: Route to end the conversation\n"
            
            # Add routing instructions
            prompt += "\nTo route to a specific agent, include their name in the following format at the end of your message: \\\\AgentName\\\\\n"
            prompt += "If you don't specify a routing, I'll choose one automatically. Only route to an agent if you think they can help with the current task."

        # add the message to our messages array
        msg = {"role": author, "content": prompt}

        # Add image file content to message
        if files:
            content = [{"type": "text", "text": prompt}]
            for file_path in files:
                # Only process image files
                if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
                    # Read image and encode it in base64
                    base64_image = self._encode_image(file_path)
                    content.append({
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    })
            msg["content"] = content

        # Add message to history
        self.messages.append(msg)

        # Format message list to be passed to the model
        messages = self.messages.copy()

        # Format the tools for the API
        tools = format_tools_for_api(self.tools, "openai") if self.tools else None

        # Print out the prompt for debugging purposes
        if show_thinking:
            self._log_thinking(prompt)

        # Call the OpenAI API based on client type (sync or async)
        if self.is_async:
            # Asynchronous call
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=tools,
                tool_choice="auto" if tools else None
            )
        else:
            # Synchronous call
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=tools,
                tool_choice="auto" if tools else None
            )

        # Extract the response text
        response_message = response.choices[0].message

        # Process tool calls if present
        if response_message.tool_calls:
            # Process each tool call
            tool_call_results = []
            for tool_call in response_message.tool_calls:
                # Find the matching tool
                tool_name = tool_call.function.name
                matching_tools = [t for t in self.tools if t.name == tool_name]
                
                if not matching_tools:
                    tool_call_results.append(f"Error: Tool '{tool_name}' not found.")
                    continue
                
                tool = matching_tools[0]
                
                # Parse the arguments
                import json
                args = json.loads(tool_call.function.arguments)
                
                # Execute the tool
                try:
                    if self.is_async:
                        # For async execution, we need to await the coroutine
                        try:
                            # The execute method might return a coroutine if the tool is async
                            result_or_coroutine = tool.execute(**args)
                            if inspect.iscoroutine(result_or_coroutine):
                                # If it's a coroutine, await it
                                result = await result_or_coroutine
                            else:
                                # If it's not a coroutine, just use it as is
                                result = result_or_coroutine
                        except Exception as e:
                            tool_call_results.append(f"Error executing {tool_name}: {str(e)}")
                            continue
                    else:
                        # For sync execution, just call the method directly
                        result = tool.execute(**args)
                        
                    tool_call_results.append(f"Result from {tool_name}: {result}")
                except Exception as e:
                    tool_call_results.append(f"Error executing {tool_name}: {str(e)}")
            
            # Add the tool call result to the messages
            self.messages.append({
                "role": "assistant",
                "content": None,
                "tool_calls": response_message.tool_calls
            })
            
            # Add the tool call results to the messages
            for idx, result in enumerate(tool_call_results):
                message = {
                    "role": "tool",
                    "tool_call_id": response_message.tool_calls[idx].id,
                    "content": result
                }
                self.messages.append(message)
            
            # Get a new response that uses the tool call results
            if self.is_async:
                # Asynchronous call 
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=self.messages
                )
            else:
                # Synchronous call
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=self.messages
                )
            
            # Update the response message
            response_message = response.choices[0].message

        # Add the response to the message history
        response_text = response_message.content
        self.messages.append({"role": "assistant", "content": response_text})

        # Print out the response for debugging purposes
        if show_thinking:
            self._log_thinking(response_text)

        return response_text


class AnthropicAgent:
    def __init__(self, client: Union[AsyncAnthropic, Anthropic], system_prompt: str, model: str = "claude-3-opus-20240229", name: str = "agent", description: str = "A general purpose agent", tools: List[Tool] = []) -> None:
        self.client = client
        self.is_async = isinstance(client, AsyncAnthropic)
        self.model = model
        self.name = name
        self.system_prompt = system_prompt
        self.description = description
        self.messages = [{"role": "system", "content": system_prompt}]
        self.tools = tools
        
    def _log_thinking(self, chat_prompt: str) -> None:
        '''
        Prints the intermediate outputs of the Agent in terminal, making thinking transparent throughout the execution of a Graph. All outputs are formatted to be clearly labelled when printed.

        Args:
            :chat_prompt (string): The prompt sent to the Agent.
        '''
        terminal_width = shutil.get_terminal_size((80, 20)).columns
        yellow = '\033[93m'
        green = '\033[92m'
        reset = '\033[0m'
        header = f" {green}{self.name}{reset} "
        visible_header = f" {header} "
        dashes = (terminal_width - len(visible_header)) // 2

        # Display agent name as header
        print(f"{yellow}{'-' * dashes}{reset}{visible_header}{yellow}{'-' * dashes}{reset}")
        
        # Helper function to enforce formatted prompts
        def format_text(text):
            formatted_lines = []
            for line in text.split("\n"):  # Preserve explicit newlines
                wrapped_lines = textwrap.wrap(line, width=terminal_width - 4)  # Wrap lines with adjusted width
                formatted_lines.extend(["    " + wrapped_line for wrapped_line in wrapped_lines])  # Add indentation
            return "\n".join(formatted_lines)

        # Display formatted prompts
        print(f"{yellow}System Prompt:{reset} {self.system_prompt}\n")
        print(f"{yellow}Chat Prompt:{reset}\n" + format_text(chat_prompt) + "\n")

    async def invoke(self, author: str, prompt: str = "", files: List[str] = [], edges: List['Agent'] = None, show_thinking: bool = False) -> str:
        '''
        Prompts the model, returning a text response. System instructions, routing options and chat history are aggregated into the prompt.

        Args:
            author (str): The role of the message sender ('user', 'assistant')
            prompt (str): Content to prompt the chat model with
            files (list[str]): List of file paths to include in the prompt
            edges (list[Agent]): Available agent routing options
            show_thinking (bool): Enables log printing of prompt and response from model

        Returns:
            str: The model's response to the prompt
        '''
        # Create a message with the prompt
        msg = {"role": author, "content": prompt}
        
        # Handle any passed files by just noting their presence in the prompt
        # This doesn't implement full RAG functionality but acknowledges the files
        if files and len(files) > 0:
            file_list = ", ".join([os.path.basename(f) for f in files])
            # Modify the prompt to include information about the files
            prompt += f"\n\n[Note: User has provided these files: {file_list}. However, file content processing is not currently available.]"
            msg = {"role": author, "content": prompt}
            
        # Add message to history
        self.messages.append(msg)

        # Format the messages list for the Anthropic API
        formatted_messages = []
        for msg in self.messages:
            formatted_messages.append(msg)

        # Add routing information as needed
        if edges and len(edges) > 1:
            routing_info = "\n\n--- Optional Routing ---\nYou can choose to route to one of the following agents:\n"
            for edge in edges:
                if edge != END:
                    routing_info += f"- {edge.name}: {edge.description}\n"
                else:
                    routing_info += f"- END: Route to end the conversation\n"
            routing_info += "\nTo route to a specific agent, include their name in the following format at the end of your message: \\\\AgentName\\\\\n"
            routing_info += "If you don't specify a routing, I'll choose one automatically. Only route to an agent if you think they can help with the current task."
            
            # Append routing info to the last message
            last_message = formatted_messages[-1]
            if isinstance(last_message["content"], str):
                formatted_messages[-1]["content"] += routing_info

        # Print out the prompt for debugging purposes
        if show_thinking:
            self._log_thinking(prompt)

        # For now, Anthropic doesn't support tools the same way as OpenAI
        if self.tools:
            print("Warning: Tool support for Anthropic is not yet fully implemented")

        # Make the API call based on client type (sync or async)
        if self.is_async:
            # Asynchronous call
            response = await self.client.messages.create(
                model=self.model,
                messages=formatted_messages,
            )
        else:
            # Synchronous call
            response = self.client.messages.create(
                model=self.model,
                messages=formatted_messages,
            )

        # Extract the response content
        response_text = response.content[0].text
        
        # Add the response to the message history
        self.messages.append({"role": "assistant", "content": response_text})

        # Print out the response for debugging purposes
        if show_thinking:
            self._log_thinking(response_text)

        return response_text