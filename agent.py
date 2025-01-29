'''
Defines individual agent types to be called within the graph structure.

Author: Jackson Grove 1/15/2025
'''
import time
from openai import OpenAI
from anthropic import Anthropic
import shutil

class Agent:
    def __init__(self, client, model: str = "gpt-4o", name: str = "agent", system_prompt: str = "You are a helpful assistant.") -> None:
        if isinstance(client, OpenAI):
            self.client = OpenAIAgent(client, system_prompt, model, name)
        elif isinstance(client, Anthropic):
            self.client = AnthropicAgent(client, system_prompt, model, name)
        else:
            raise ValueError("Client must be an instance of OpenAI or Anthropic")
        self.model = self.client.model
        self.name = self.client.name
        self.system_prompt = self.client.system_prompt
        self.messages = self.client.messages

        
    def invoke(self, author: str, prompt: str, show_thinking: bool = False) -> str:
        return self.client.invoke(author, prompt, show_thinking)


class OpenAIAgent:
    def __init__(self, client: OpenAI, system_prompt: str, model: str = "gpt-4o", name: str = "agent") -> None:
        self.client = client
        self.model = model
        self.name = name
        self.system_prompt = system_prompt
        self.messages = [
            {"role": "system", "content": system_prompt}
        ]


    def invoke(self, author: str, chat_prompt: str = "", show_thinking: bool = False) -> str:
        '''
        Prompts the model, returning a text response

        Args:
            :chat_prompt (string): The prompt to send to the model.

        Returns:
            Text response from the model (string)
        '''
        assert author in ['system', 'assistant', 'user', 'function', 'tool', 'developer'], f"Invalid value: '{author}'. Supported values are: system, assistant, user, function, tool, developer"
        
        if show_thinking:
            # Log the formatted system prompt and chat prompt
            terminal_width = shutil.get_terminal_size((80, 20)).columns
            yellow = '\033[93m'
            green = '\033[92m'
            reset = '\033[0m'
            header = f"\n {green}{self.name}{reset} "
            visible_header = f" {reset}{header}{yellow} "
            dashes = (terminal_width - (len(visible_header) + len(yellow) + len(reset))) // 2
            print(f"{yellow}{'-' * dashes}{visible_header}{'-' * dashes}{reset}")
            print(f"{yellow}System Prompt:{reset} {self.system_prompt}\n")
            print(f"{yellow}Chat Prompt:{reset} {chat_prompt}\n")

        # Add message to thread
        self.messages.append(
            {"role": author, "content": chat_prompt}
        )
        
        # Create a run to execute newly added message
        response = self.client.chat.completions.create(
            model=self.model,
            messages=self.messages
        )
        return response.choices[0].message.content
    

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