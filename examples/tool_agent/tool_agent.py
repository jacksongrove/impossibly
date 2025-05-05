import os
from dotenv import load_dotenv
from openai import AsyncOpenAI
from imagination_engine import Agent, Graph, START, END, Tool

# Define our tools
def calculate_sum(a, b):
    """Calculate the sum of two numbers."""
    result = a + b
    return result

def get_current_time():
    """Get the current time in a readable format."""
    from datetime import datetime
    result = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return result

def count_rs(text):
    """Count the number of 'R's (case-insensitive) in the provided text."""
    # Count uppercase R's
    uppercase_count = text.count('R')
    # Count lowercase r's
    lowercase_count = text.count('r')
    # Total count (both uppercase and lowercase)
    result = uppercase_count + lowercase_count
    return result

def __main__():
    # Load environment variables from .env file
    load_dotenv()
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    if not OPENAI_API_KEY:
        raise ValueError("OpenAI API key is not set. Please check your .env file.")

    # Initialize the OpenAI client
    client = AsyncOpenAI(api_key=OPENAI_API_KEY)

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
            function=count_rs,
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