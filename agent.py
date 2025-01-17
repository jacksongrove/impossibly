'''
Defines individual agent types to be called within the graph structure.

Author: Jackson Grove 1/15/2025
'''
import time
from openai import OpenAI

class Agent:
    def __init__(self, client, model="gpt-4o", name="agent", system_prompt="You are a helpful assistant."):
        self.client = client
        self.model = model
        self.name = name
        self.system_prompt = system_prompt
        self.assistant_id = self._create_assistant()
        self.thread_id = self._create_thread()
    
    def _create_assistant(self):
        '''
        Creates an OpenAI Assistant, returning its Assistant ID

        Returns:
            The Agent's Assistant ID for later reference and usage (string)
        '''
        assistant = self.client.beta.assistants.create(
            name=self.name,
            instructions=self.system_prompt,
            model=self.model
        )
        return assistant.id

    def _create_thread(self):
        '''
        Creates a thread for the Agent to track messages

        Returns:
            The Agent's Thread ID for later reference and usage (string)
        '''
        thread = self.client.beta.threads.create(
            messages=[]
        )
        return thread.id

    def invoke(self, chat_prompt=""):
        '''
        Prompts the model, returning a text response

        Args:
            :chat_prompt (string): The prompt to send to the model.

        Returns:
            Text response from the model (string)
        '''
        # Add message to thread
        message = self.client.beta.threads.messages.create(
            thread_id=self.thread_id,
            role="user",
            content=chat_prompt
        )
        
        # Create a run to execute newly added message
        run = self.client.beta.threads.runs.create(
            thread_id=self.thread_id,
            assistant_id=self.assistant_id,
            instructions=chat_prompt,
        )
        run_id = run.id

        # Wait until the run is complete
        run = self.client.beta.threads.runs.retrieve(
            thread_id=self.thread_id,
            run_id=run_id
        )
        while run.status in ['in_progress', 'queued']:
            # Query again to update run status
            run = self.client.beta.threads.runs.retrieve(
                thread_id=self.thread_id,
                run_id=run_id
            )
            time.sleep(.1)
        
        # Handle run completion once finished
        if run.status == 'completed':
            messages = self.client.beta.threads.messages.list(
                thread_id=self.thread_id
            )
            return messages.data[0].content[0].text.value
        elif run.status == 'requires_action':
            print("requires an action") # TODO: Code to call actions & route responses
        elif run.status == 'expired':
            raise TimeoutError('The run execution expired. Try again.')
        elif run.status == 'failed':
            raise TimeoutError('The run execution failed. Try again.')
        elif run.status == 'incomplete':
            raise TimeoutError('The run execution never completed. Try again.')
        elif run.status == 'cancelling':
            print("The run execution is cancelling.")
            pass
        elif run.status == 'cancelled':
            print("The run execution was cancelled.")
            pass
        else:
            raise ValueError(f"Unexpected value for Run status: {run.status}")
