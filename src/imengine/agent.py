'''
Defines individual agent types to be called within the graph structure.

Author: Jackson Grove
'''
import re
import shutil
import textwrap
from openai import OpenAI
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

    def __init__(self, client, model: str = "gpt-4o", name: str = "agent", system_prompt: str = "You are a helpful assistant.", description: str = "", shared_memory: list['Agent'] = None) -> None:
        if isinstance(client, OpenAI):
            self.client = OpenAIAgent(client, system_prompt, model, name, description)
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

        
    def invoke(self, author: str, prompt: str, edges: list['Agent'] = None, show_thinking: bool = False) -> str:
        return self.client.invoke(author, prompt, edges, show_thinking)


class OpenAIAgent:
    def __init__(self, client: OpenAI, system_prompt: str, model: str = "gpt-4o", name: str = "agent", description: str = "A general purpose agent", routing_instructions: str = "") -> None:
        self.client = client
        self.model = model
        self.name = name
        self.system_prompt = system_prompt
        self.description = description
        self.routing_instructions = routing_instructions
        self.messages = [
            {"role": "system", "content": system_prompt}
        ]


    def invoke(self, author: str, chat_prompt: str = "", edges: list['Agent'] = None, show_thinking: bool = False) -> str:
        '''
        Prompts the model, returning a text response. System instructions, routing options and chat history are aggregated into the prompt in the following format:

            System Instructions:
                {system_prompt}

            Chat Prompt:
                {chat_prompt}

            Previous conversations:
                {example agent 1} -> {example agent 2}: {content}
                {example agent 1} -> {example agent 3}: {content}
                {example agent 2} -> {example agent 1}: {content}
                (rest of chat history continued...  NOTE: This section will only appear if the agent has a shared memory with other agents. The Agent conversations that appear will be limited to 
                those in the shared_memory attribute)

            Routing Options:
                Print ONE of the following commands after your response to send your response to that agent. You are required to choose one.

                '\\\\option1\\\\'  Description: {description}
                '\\\\option2\\\\'  Description: {description}
                (rest of routing options continued...)
        
        This is all encapsulated in the list of threaded message history then passed to the model.

        Args:
            :chat_prompt (string): The prompt to send to the model.
            :edges (list[Agent]): A list of agents to route to.
            :show_thinking (bool): Whether to print the system prompt and chat prompt to the console.

        Returns:
            Text response from the model (string)
        '''
        assert author in ['system', 'assistant', 'user', 'function', 'tool', 'developer'], f"Invalid value: '{author}'. Supported values are: system, assistant, user, function, tool, developer"
        
        if show_thinking:
            # Log the formatted system prompt and chat prompt
            self._log_thinking(chat_prompt)

        # Define routing options & commands
        routing_options = ""
        if edges and len(edges) > 1:
            routing_options = "Routing Options:\nPrint ONE of the following commands after your response to send your response to that agent. You are required to choose one.\n\n"
            for agent in edges:
                routing_options += f"\nCommand: '\\\\{agent.name if agent is not END else 'END'}\\\\'\tDescription: {agent.description if agent is not END else 'The end of the graph, to return the final response to the user.'}"

        # Add message to thread
        self.messages.append(
            {"role": author, "content": f'System Prompt: {self.system_prompt}\n\nChat Prompt: {chat_prompt}\n\n{routing_options}'} # TODO: Implement optional routing instructions for additional logic
        )
        
        # Create a run to execute newly added message
        response = self.client.chat.completions.create(
            model=self.model,
            messages=self.messages
        )
        return response.choices[0].message.content
    

    def _log_thinking(self, chat_prompt: str) -> None:
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