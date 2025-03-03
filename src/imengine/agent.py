'''
Defines individual agent types to be called within the graph structure.

Author: Jackson Grove
'''
import os, shutil, textwrap, base64
from openai import OpenAI
from openai import File
from anthropic import Anthropic
from utils.start_end import END
from utils.memory import Memory

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

    Attributes:
        client: The underlying agent instance (either OpenAIAgent or AnthropicAgent).
        model (str): The identifier of the language model.
        name (str): The name of the agent.
        system_prompt (str): The system prompt configuring the agent's behavior.
        description (str): An additional description for the agent.
        shared_memory (list of Agents): A list of agents to read memory from.

    Raises:
        ValueError: If the provided client is not an instance of either OpenAI or Anthropic.
    '''

    def __init__(self, client, model: str = "gpt-4o", name: str = "agent", system_prompt: str = "You are a helpful assistant.", description: str = "", files: list[str] = [], shared_memory: list['Agent'] = None) -> None:
        if isinstance(client, OpenAI):
            self.client = OpenAIAgent(client, system_prompt, model, name, description, files)
        elif isinstance(client, Anthropic):
            self.client = AnthropicAgent(client, system_prompt, model, name, description)
        else:
            raise ValueError("Client must be an instance of OpenAI or Anthropic")
        self.model = self.client.model
        self.name = self.client.name
        self.system_prompt = self.client.system_prompt
        self.messages = self.client.messages
        self.description = self.client.description
        self.shared_memory = shared_memory
        self.files = self.client.files

        
    def invoke(self, author: str, prompt: str, files: list[str] = [], edges: list['Agent'] = None, show_thinking: bool = False) -> str:
        return self.client.invoke(author, prompt, files, edges, show_thinking)


class OpenAIAgent:
    def __init__(self, client: OpenAI, system_prompt: str, model: str = "gpt-4o", name: str = "agent", description: str = "A general purpose agent", routing_instructions: str = "", files: list[str] = []) -> None:
        self.client = client
        self.model = model
        self.name = name
        self.system_prompt = system_prompt
        self.description = description
        self.routing_instructions = routing_instructions
        self.messages = [
            {"role": "system", "content": system_prompt}
        ]
        self.files = self.init_rag_files(files)


    def init_rag_files(self, files: list[str]) -> list['File']:
        '''
        Initializes and uploads files for Retrieval-Augmented Generation (RAG) purposes.

        This method processes a list of file paths, validates their extensions against a predefined set of supported file types, and uploads them to the OpenAI API with the purpose set to 
        "assistants". Uploaded files are returned as OpenAI File objects.

        Args:
            files (list[str]): A list of file paths to be uploaded for RAG purposes.

        Returns:
            list[File]: A list of OpenAI File objects created by the OpenAI API.

        Raises:
            AssertionError: If a file's extension is not in the supported file types.
            Exception: If an error occurs during the file upload process.

        Notes:
            - Supported file types include text documents, images, code files, and other formats compatible with RAG workflows (e.g., `.txt`, `.pdf`, `.json`).
            - Files with unsupported extensions are skipped, and an error message is logged.
            - Ensure the provided file paths are valid and accessible.
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
                    f"Unsupported file type '{ext}'. Accepted types: {", ".join(supported_files.keys())}"
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
    

    def init_input_files(self, files: list[str]) -> list['File']:
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


    def invoke(self, author: str, chat_prompt: str = "", files: list[str] = [], edges: list['Agent'] = None, show_thinking: bool = False) -> str:
        '''
        Prompts the model, returning a text response. System instructions, routing options and chat history are aggregated into the prompt in the following format:
            """
            ## System Instructions:
                {system_prompt}

            ## Chat Prompt:
                {chat_prompt}
            
            >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
            ## Previous conversations:
                {example agent 1} -> {example agent 2}: {content}
                {example agent 1} -> {example agent 3}: {content}
                {example agent 2} -> {example agent 1}: {content}
                (rest of chat history continued...  NOTE: This section will only appear if the agent has a shared memory with other agents. The Agent conversations that appear will be limited to 
                those in the shared_memory attribute)
            <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

            ## File options:
                Select the files you'd like to pass to the next agent. You can select more than one or none at all.
                Command: <<FILE>>option1<</FILE>>
                Command: <<FILE>>option2<</FILE>>
                (rest of file options continued...)

            ## Routing Options:
                Print ONE of the following commands after your response to send your response to that agent. You are required to choose one.
                Command: '\\\\option1\\\\'  Description: {description}
                Command: '\\\\option2\\\\'  Description: {description}
                (rest of routing options continued...)
            """
        NOTE: This is all encapsulated in the list of threaded message history then passed to the model.

        Args:
            :chat_prompt (string): The prompt to send to the model.
            :edges (list[Agent]): A list of agents to route to.
            :show_thinking (bool): Whether to print the system prompt and chat prompt to the console.

        Returns:
            Text response from the model (string)
        '''
        assert author in ['system', 'assistant', 'user', 'function', 'tool', 'developer'], f"Invalid value: '{author}'. Supported values are: system, assistant, user, function, tool, developer"
        # Create File objects, designating for vision if file type is vision-compatable, otherwise use for RAG
        file_objs = self.init_input_files(files) if files else [] # Base64 encode
        processed_image_files = []
        for i, file in enumerate(file_objs):
            if file.purpose == "vision":
                encoded_file = self._encode_image(files[i]) # Pass the file path to be encoded as a Base64 string
                processed_image_files.append(encoded_file)
            elif file.purpose == "assistants": #TODO: Implement RAG for non-image files
                continue

        if show_thinking:
            # Log the formatted system prompt and chat prompt
            self._log_thinking(chat_prompt)

        # Build routing options & respective commands
        routing_options = ""
        if edges and len(edges) > 1:
            routing_options = "## Routing Options:\n\tPrint ONE of the following commands after your response to send your response to that agent. You are required to choose one."
            for agent in edges:
                routing_options += f"\n\tCommand: '\\\\{agent.name if agent is not END else 'END'}\\\\'\tDescription: {agent.description if agent is not END else 'The end of the graph, to return the final response to the user.'}"
        else:
            routing_options = f"## Routing Disclosure: Your response will be routed to '{edges[0].name if edges[0] is not END else 'END'}'\tDescription: {edges[0].description if edges[0] is not END else 'The end of the graph, to return the final response to the user.'}"
        # Build file propagation options & respective commands
        file_propagation = ""
        if files:
            file_propagation = "## File Options:\n\tSelect the files you'd like to pass to the next agent. You can select more than one or none at all by typing these commands in your response."
            for file in files:
                file_propagation += f"\n\tCommand: <<FILE>>{file}<</FILE>>"

        # Add message to thread
        content_payload = []
        # Add the text component
        content_payload.append({
            "type": "text",
            "text": f'## System Prompt: {self.system_prompt}\n\n## Chat Prompt: {chat_prompt}\n\n{file_propagation}\n\n{routing_options}'
        })

        # Append each vision image in the correct format
        for encoded_image in processed_image_files:
            content_payload.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{encoded_image}"}
            })
        
        self.messages.append({
            "role": author,
            "content": content_payload
        })
        
        # Create a run to execute newly added message
        response = self.client.chat.completions.create(
            model=self.model,
            messages=self.messages
        )
        return response.choices[0].message.content


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
    

class AnthropicAgent:
    def __init__(self, client: Anthropic, system_prompt: str, model: str = "claude-3-5-sonnet-20240620", name: str = "agent") -> None:
        self.client = client
        self.model = model
        self.name = name
        self.system_prompt = system_prompt
        self.messages = [{"role": "system", "content": system_prompt}]

    def invoke(self, author: str, chat_prompt: str = "", show_thinking: bool = False) -> str:
        '''
        Prompts the model, returning a text response

        Args:
            :chat_prompt (string): The prompt to send to the model.
        '''
        pass