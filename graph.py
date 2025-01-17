'''
Graph.py

Initializing the graph structure to define the order in which agents execute and how agents 
communicate with one another.

Author: Jackson Grove 1/15/2025
'''
import os
from dotenv import load_dotenv
from agent import *

def __main__():
    # Load environment variables
    load_dotenv()
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    if not OPENAI_API_KEY:
        raise ValueError("OpenAI API key is not set. Please check your .env file.")

    # Initalize client
    client = OpenAI(api_key=OPENAI_API_KEY)

    # Initalize Agent objects
    agent = Agent(client, system_prompt="You are a helpful assistant.")

    # Call agent
    response = agent.invoke("Write a haiku about recursion in programming.")
    print(response)
    

if __name__ == "__main__":
    __main__()