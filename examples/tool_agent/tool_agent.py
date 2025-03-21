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
from utils.tools import Tool

# Define our tools
def calculate_sum(a, b):
    """Calculate the sum of two numbers."""
    return a + b

def get_current_time():
    """Get the current time in a readable format."""
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def count_rs(text):
    """Count the number of 'R's (case-insensitive) in the provided text."""
    return text.lower().count('r')

def __main__():
    # Load environment variables from .env file
    load_dotenv()
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    if not OPENAI_API_KEY:
        raise ValueError("OpenAI API key is not set. Please check your .env file.")

    # Initialize the OpenAI client
    from openai import OpenAI
    client = OpenAI(api_key=OPENAI_API_KEY)

    # Define our tools
    # Tool with no parameters
    get_current_time_tool = Tool(
        name="get_current_time",
        description="Get the current time",
        function=get_current_time
    )
        
    # Tool with one string parameter
    count_rs_tool = Tool(
            name="count_rs",
            description="Count the number of 'R's in the provided text",
            function=lambda text: text.lower().count('r'),
            parameters=[
                {
                    "name": "text",
                    "type": str,
                    "description": "The text in which to count the 'R's"
                }
            ]
        )

    # Tool with two float parameters
    calculate_sum_tool = Tool(
        name="calculate_sum",
        description="Calculate the sum of two numbers",
        function=calculate_sum,
        parameters=[
                {
                    "name": "a",
                    "type": float,
                    "description": "First number"
                },
                {
                    "name": "b",
                    "type": float,
                    "description": "Second number"
                }
            ]
        )
    
    # Initialize Agent with tools
    agent = Agent(
        client, 
        model="gpt-4o", 
        name="ToolAgent", 
        system_prompt="""
            You are an agent that can use various tools to help users. You can:
            1. Calculate sums using the calculate_sum tool
            2. Get the current time using the get_current_time tool
            3. Count the number of 'R's in the provided text using the count_rs tool

            When a user asks for something that requires using a tool, use the appropriate tool and explain what you're doing.
            Always provide clear explanations of your actions and the results.
        """,
        description="A helpful agent that can use various tools to assist users",
        tools=[get_current_time_tool, count_rs_tool, calculate_sum_tool]
    )

    # Initialize and build the graph
    graph = Graph()
    graph.add_node(agent)
    graph.add_edge(START, agent)
    graph.add_edge(agent, END)

    # Test prompts for each tool
    response = graph.invoke("What is 5 plus 3?", show_thinking=True)
    print(f"Response: {response}")
    response = graph.invoke("What time is it?", show_thinking=True)
    print(f"Response: {response}")
    response = graph.invoke("How many R's are in the word 'strawberry'?", show_thinking=True)
    print(f"Response: {response}")

if __name__ == "__main__":
    __main__() 