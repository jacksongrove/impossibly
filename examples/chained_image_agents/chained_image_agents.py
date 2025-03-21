import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Get directory paths to interact with library modules. This will be changed to a package import in the future.
BASE_DIR = Path(__file__).resolve().parent.parent.parent
LIB_DIR = BASE_DIR / 'src' / 'imengine'
sys.path.insert(0, str(LIB_DIR))

# Import modules
from agent import Agent
from graph import Graph
from utils.start_end import START, END

def __main__():
    # Load environment variables from .env file
    load_dotenv()
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    if not OPENAI_API_KEY:
        raise ValueError("OpenAI API key is not set. Please check your .env file.")

    # Initialize the OpenAI client
    from openai import OpenAI
    client = OpenAI(api_key=OPENAI_API_KEY)

    # Initialize Agents
    agent = Agent(
        client, 
        model="gpt-4o", 
        name="agent", 
        system_prompt="You are a helpful assistant that sends images as proof when necessary.",
    )

    untrusting = Agent(
        client, 
        model="gpt-4o", 
        name="untrusting", 
        system_prompt="You don't believe anything anyone tells you so you always want to double check.",
        description="This agent is untrusting so it needs proof for everything told to it. Its response will be outputted to the user."
    )

    # Initialize and build the graph
    graph = Graph()
    graph.add_node(agent)
    graph.add_node(untrusting)

    graph.add_edge(START, agent)
    graph.add_edge(agent, untrusting)
    graph.add_edge(untrusting, END)

    # Invoke the graph with an example prompt and show the thinking process
    response = graph.invoke("What is in this image?", files = ['examples/image_input.jpeg'], show_thinking=True)
    print(response)

if __name__ == "__main__":
    __main__()