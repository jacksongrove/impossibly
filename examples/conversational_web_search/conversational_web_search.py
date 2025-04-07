"""
Example of conversational web search agents using the imagination-engine framework.
This example demonstrates two web search agents that can talk to each other about topics
that require web searches, using the Tavily API for real-time information.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Get directory paths to interact with library modules. This will be replaced by the package import in the future.
BASE_DIR = Path(__file__).resolve().parent.parent.parent
LIB_DIR = BASE_DIR / 'src'
sys.path.insert(0, str(LIB_DIR))

# Import modules
from imengine import Agent, Graph, Tool, START, END

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

def __main__():
    # Load environment variables from .env file
    load_dotenv()
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    if not OPENAI_API_KEY:
        raise ValueError("OpenAI API key is not set. Please check your .env file.")
    
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
    if not TAVILY_API_KEY:
        raise ValueError("Tavily API key is not set. Please check your .env file.")

    # Initialize the OpenAI client
    from openai import OpenAI
    client = OpenAI(api_key=OPENAI_API_KEY)

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
    
    # Initialize the first web search agent (Researcher)
    researcher = Agent(
        client, 
        model=os.getenv("MODEL_NAME", "gpt-4-turbo-preview"), 
        name="Researcher", 
        system_prompt="""
            You are a Research Agent specialized in gathering and analyzing information from the web.
            Your role is to search for information, analyze it, and provide insights to the other agent.
            
            When you receive a query:
            1. Use the web_search tool to find relevant information
            2. Format the search results using the format_search_results tool
            3. Analyze the information and provide your insights
            4. Engage in a conversation with the other agent, asking questions or providing information
            5. Always cite your sources and be transparent about the information you find
            
            You should be thorough, analytical, and focused on gathering comprehensive information.
            When talking to the other agent, be collaborative and help build on each other's insights.
        """,
        description="A research agent that searches for and analyzes information from the web",
        tools=[web_search_tool, format_results_tool]
    )
    
    # Initialize the second web search agent (Analyst)
    analyst = Agent(
        client, 
        model=os.getenv("MODEL_NAME", "gpt-4-turbo-preview"), 
        name="Analyst", 
        system_prompt="""
            You are an Analysis Agent specialized in interpreting and synthesizing information.
            Your role is to take the information provided by the Researcher, analyze it further, and provide deeper insights.
            
            When you receive information:
            1. Use the web_search tool to find additional information if needed
            2. Format the search results using the format_search_results tool
            3. Analyze the information and provide your insights
            4. Engage in a conversation with the other agent, asking questions or providing information
            5. Always cite your sources and be transparent about the information you find
            
            You should be critical, insightful, and focused on providing deeper analysis and interpretation.
            When talking to the other agent, be collaborative and help build on each other's insights.
        """,
        description="An analysis agent that interprets and synthesizes information from the web",
        tools=[web_search_tool, format_results_tool]
    )
    
    # Initialize the summarizer agent
    summarizer = Agent(
        client, 
        model=os.getenv("MODEL_NAME", "gpt-4-turbo-preview"), 
        name="Summarizer", 
        system_prompt="""
            You are a Summarizer Agent. Your task is to distill complex or lengthy responses into clear, concise summaries 
            that capture the full nuance of the conversation, including previous messages.

            When you receive a response:
            1. Reformat and condense the content into coherent sentences or paragraphs. This is your default behavior.
            2. Preserve all essential details, nuances, and insights.
            3. Remove redundant or extraneous information while maintaining the original message's intent.
            4. Present the summary in a narrative format without using bullet points.

            Do not reference agent outputs or previous messages explicitly. Speak directly to the user using only the 
            conversation content.

            Your output should be succinct and comprehensive, enabling the user to quickly grasp the core ideas.
        """,
        description="This agent is a summarizer that will make input clear and return it to the user.",
        shared_memory=[researcher, analyst]
    )

    # Initialize and build the graph
    graph = Graph()
    graph.add_node(researcher)
    graph.add_node(analyst)
    graph.add_node(summarizer)

    # Connect the agents in a conversational flow
    graph.add_edge(START, researcher)
    graph.add_edge(researcher, analyst)
    graph.add_edge(analyst, researcher)  # Allow for back-and-forth conversation
    graph.add_edge(researcher, summarizer)
    graph.add_edge(analyst, summarizer)
    graph.add_edge(summarizer, END)

    # Test prompts
    response = graph.invoke("What are the latest developments in quantum computing? Have a detailed conversation about this topic.", show_thinking=True)
    print(f"Response: {response}")
    
    response = graph.invoke("What are the ethical implications of artificial intelligence? Discuss this topic in depth.", show_thinking=True)
    print(f"Response: {response}")
    
    response = graph.invoke("What are the current challenges and solutions for climate change? Have a thorough discussion about this.", show_thinking=True)
    print(f"Response: {response}")

if __name__ == "__main__":
    __main__() 