import os
from pathlib import Path
from dotenv import load_dotenv
from impossibly import Agent, Graph, START, END

# Define the path to the image file
IMAGE_PATH = Path(__file__).parent / "image_input.jpeg"


def __main__():
    # Load environment variables from .env file
    load_dotenv()
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    if not OPENAI_API_KEY:
        raise ValueError(
            "OpenAI API key is not set. Please check your .env file."
        )

    # Check if the image file exists
    if not IMAGE_PATH.exists():
        raise FileNotFoundError(f"Image file not found at {IMAGE_PATH}")

    # Initialize the OpenAI client
    from openai import OpenAI
    client = OpenAI(api_key=OPENAI_API_KEY)

    # Initialize Agents
    agent = Agent(
        client,
        model="gpt-4o",
        name="agent",
        system_prompt="You are a helpful assistant",
    )

    # Initialize and build the graph
    graph = Graph()
    graph.add_node(agent)
    graph.add_edge(START, agent)
    graph.add_edge(agent, END)

    # Invoke the graph with an example prompt and show the thinking process
    response = graph.invoke(
        "What's this an image of?", files=[str(IMAGE_PATH)], show_thinking=True
    )
    print(response)


if __name__ == "__main__":
    __main__()
