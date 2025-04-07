"""
Example of a single web search agent using the imagination-engine framework with Tavily integration.
This agent can perform web searches and provide information based on the search results.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Get directory paths to interact with library modules. This will be changed to a package import in the future.
BASE_DIR = Path(__file__).resolve().parent.parent.parent
LIB_DIR = BASE_DIR / 'src'
sys.path.insert(0, str(LIB_DIR))

# Import modules
from imengine.agent import Agent
from imengine.graph import Graph
from imengine.utils.start_end import START, END
from imengine.utils.tools import Tool

# Load environment variables
load_dotenv()

def perform_web_search(query, max_results=5):
    """
    Perform a web search using Tavily API and return the results.
    
    Args:
        query (str): The search query
        max_results (int): Maximum number of results to return
        
    Returns:
        dict: The search results from Tavily
    """
    from tavily import TavilyClient
    
    # Initialize Tavily client
    tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
    
    # Perform the web search
    search_results = tavily_client.search(
        query=query,
        max_results=max_results,
        search_depth="advanced",  # Use advanced search for more comprehensive results
        include_answer=True,  # Include an AI-generated answer in the response
        include_raw_content=False,  # Don't include raw HTML content
        include_images=False,  # Don't include images
        include_image_descriptions=False,  # Don't include image descriptions
        include_domains=[],  # No specific domains to include
        exclude_domains=[]  # No specific domains to exclude
    )
    
    return search_results

def format_search_results(search_results, query):
    """
    Format the search results into a prompt for the agent.
    
    Args:
        search_results (dict): The search results from Tavily
        query (str): The original search query
        
    Returns:
        str: Formatted prompt for the agent
    """
    # Format the search results into a prompt
    formatted_results = "Here are the search results for your query:\n\n"
    
    # Add the AI-generated answer if available
    if search_results.get("answer"):
        formatted_results += f"AI-Generated Answer: {search_results['answer']}\n\n"
    
    # Add the search results
    for i, result in enumerate(search_results.get("results", []), 1):
        formatted_results += f"Source {i}:\n"
        formatted_results += f"Title: {result.get('title', 'N/A')}\n"
        formatted_results += f"URL: {result.get('url', 'N/A')}\n"
        formatted_results += f"Content: {result.get('content', 'N/A')}\n"
        formatted_results += f"Relevance Score: {result.get('score', 'N/A')}\n\n"

    # Add the user's original query
    formatted_results += f"\nBased on these search results, please answer: {query}"
    
    return formatted_results

def main():
    # Load environment variables from .env file
    load_dotenv()
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    if not OPENAI_API_KEY:
        raise ValueError("OpenAI API key is not set. Please check your .env file.")
    
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
    if not TAVILY_API_KEY:
        raise ValueError("Tavily API key is not set. Please check your .env file.")

    # Initialize the OpenAI client
    from openai import AsyncOpenAI
    client = AsyncOpenAI(api_key=OPENAI_API_KEY)

    # Define our web search tool
    web_search_tool = Tool(
        name="web_search",
        description="Perform a web search using Tavily API",
        function=perform_web_search,
        parameters=[
            {
                "name": "query",
                "type": str,
                "description": "The search query"
            },
            {
                "name": "max_results",
                "type": int,
                "description": "Maximum number of results to return",
                "default": 5
            }
        ]
    )
    
    # Define our format results tool
    format_results_tool = Tool(
        name="format_search_results",
        description="Format search results into a prompt for the agent",
        function=format_search_results,
        parameters=[
            {
                "name": "search_results",
                "type": dict,
                "description": "The search results from Tavily"
            },
            {
                "name": "query",
                "type": str,
                "description": "The original search query"
            }
        ]
    )
    
    # Initialize Agent with tools
    agent = Agent(
        client, 
        model=os.getenv("MODEL_NAME", "gpt-4-turbo-preview"), 
        name="WebSearchAgent", 
        system_prompt="""
            You are a web search assistant that helps users find information from the internet.
            When given a query, you will:
            1. Use the provided search results to answer the user's question
            2. Always cite your sources
            3. Provide a comprehensive but concise response
            4. If the search results don't contain enough information, acknowledge this limitation

            Remember to be helpful, accurate, and transparent about your sources.
        """,
        description="An agent that performs web searches and provides information based on the results",
        tools=[web_search_tool, format_results_tool]
    )

    # Initialize and build the graph
    graph = Graph()
    graph.add_node(agent)
    graph.add_edge(START, agent)
    graph.add_edge(agent, END)

    # Test prompts
    response = graph.invoke("What are the latest developments in quantum computing?", show_thinking=True)
    print(f"Response: {response}")
    
    response = graph.invoke("Who is the current CEO of OpenAI?", show_thinking=True)
    print(f"Response: {response}")
    
    response = graph.invoke("What are the main features of Python 3.12?", show_thinking=True)
    print(f"Response: {response}")

if __name__ == "__main__":
    main() 