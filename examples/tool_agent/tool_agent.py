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
from utils.tools import Tool, Parameter, ParameterType

# Define our tools
def calculate_sum(a: float, b: float) -> float:
    """Calculate the sum of two numbers."""
    return a + b

def get_current_time() -> str:
    """Get the current time in a readable format."""
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def search_web(query: str) -> str:
    """Search the web for a given query. This is a mock implementation."""
    return f"Search results for '{query}': [This is a mock search result]"

def __main__():
    # Load environment variables from .env file
    load_dotenv()
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    if not OPENAI_API_KEY:
        raise ValueError("OpenAI API key is not set. Please check your .env file.")

    # Initialize the OpenAI client
    from openai import OpenAI
    client = OpenAI(api_key=OPENAI_API_KEY)

    # Define available tools
    calculator_tool = Tool(
        name="calculate_sum",
        description="Calculate the sum of two numbers",
        function=calculate_sum,
        parameters=[
            Parameter(
                name="a",
                type=ParameterType.NUMBER,
                description="First number"
            ),
            Parameter(
                name="b",
                type=ParameterType.NUMBER,
                description="Second number"
            )
        ]
    )
    get_time_tool = Tool(
        name="get_current_time",
        description="Get the current time",
        function=get_current_time
    )
    web_search_tool = Tool(
        name="search_web",
        description="Search the web for a given query",
        function=search_web,
        parameters=[
            Parameter(
                name="query",
                type=ParameterType.STRING,
                description="The search query"
            )
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
            3. Search the web using the search_web tool

            When a user asks for something that requires using a tool, use the appropriate tool and explain what you're doing.
            Always provide clear explanations of your actions and the results.
        """,
        description="A helpful agent that can use various tools to assist users",
        tools=[calculator_tool, get_time_tool, web_search_tool] # Add all our tools to the agent
    )

    # Initialize and build the graph
    graph = Graph()
    graph.add_node(agent)
    graph.add_edge(START, agent)
    graph.add_edge(agent, END)

    # Test all 3 functions with 3 different prompts
    response = graph.invoke("What is 5 plus 3?", show_thinking=True)
    print(f"Response: {response}")
    response = graph.invoke("What time is it?", show_thinking=True)
    print(f"Response: {response}")
    response = graph.invoke("Search for information about artificial intelligence", show_thinking=True)
    print(f"Response: {response}")

if __name__ == "__main__":
    __main__() 