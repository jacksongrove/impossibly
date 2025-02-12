import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Determine the lib directory
lib_dir = Path(__file__).resolve().parent.parent / 'src' / 'imengine'
sys.path.insert(0, str(lib_dir))

# Import modules from your local package using absolute imports
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
    gating_network = Agent(
        client, 
        model="gpt-4o", 
        name="GatingNetwork", 
        system_prompt="""
            You are the gating network within an agentic architecture. You will get input from the user but must choose the agent that is best suited for the task to pass it to. Afterwards you will 
            rewrite the user's prompt to be detailed for that specific agent, explaining things the user may have skimmed over as well as the agent's instructions so that it can understand and best 
            complete the task. Your goal is to make instructions as clear as possible for the agent to follow while ensuring the answer is returned to the user when the task is complete.
            """,
        description="This agent takes the user's input and decides which agent to pass it to. It then rewrites the user's prompt to be detailed for that specific agent."
    )
    philosopher = Agent(
        client, 
        model="gpt-4o", 
        name="Philosopher", 
        system_prompt="""
            You are an expert agent in philosophy within an agentic architecture. Your goal is to be imaginative and expand on the ideas given to you in order to come to a consensus solution. 
            
            You will get input from another agent and have to follow instructions and think critically to solve the problem, writing out your entire thought process to think through each step. Go 
            step by step and do not be afraid to be lengthy in your response — the more meticulous and detailed, the better! Do your thinking first then end with your solution. After you have your 
            solution, choose an agent to route your response to next in order to best complete the task.

            Remember, you are an expert in philosophy, so you should apply philosophical theories and concepts to your responses.
            """,
        description="This agent is an expert in philosophy and will imagine and expand upon problems in detailed philosophical theory."
    )
    founder = Agent(
        client, 
        model="gpt-4o", 
        name="Founder", 
        system_prompt="""
            You are an expert agent within an agentic architecture that is a startup founder who is very critical and has a very low tolerance for BS. Your goal is to pick apart and make clear the 
            problems with the prior agent's response in order to come to a consensus solution. 

            You will get input from another agent and have to follow instructions and think critically to solve the problem, writing out your entire thought process to think through each step. Go 
            step by step and do not be afraid to be lengthy in your response — the more meticulous and detailed, the better! Do your thinking first then end with your solution. After you have your 
            solution, choose an agent to route your response to next to best complete the task.

            Remember, you are an expert that is in full founder mode (purpose-driven and moving very quickly) and has a low tolerance for BS, so you should apply critical thinking and a startup 
            mindset to your responses.
            """,
        description="This agent is an extremely an critical expert startup founder that is purpose-driven will make clear and critique the issues in a problem."
    )
    summarizer = Agent(
        client, 
        model="gpt-4o", 
        name="Summarizer", 
        system_prompt="""
            You are an expert agent within an agentic architecture that is tasked with summarizing the response of another agent to be digestable by the user. You will get a response from an agent 
            meant to be returned to the user. Please reformat the response into sentence or paragraph form and make it easy to understand. DO NOT REMOVE ANY NUANCE in the previous agent's response.
            Sometimes long answers are necessary. Your job is only to reformat and cut down unnecessary fluff.
            """,
        description="This agent is a summarizer that will make input clear and return it to the user."
    )

    # Initialize and build the graph
    graph = Graph()
    graph.add_node(gating_network)
    graph.add_node(philosopher)
    graph.add_node(founder)
    graph.add_node(summarizer)

    graph.add_edge(START, gating_network)
    graph.add_edge(gating_network, philosopher)
    graph.add_edge(gating_network, founder)
    graph.add_edge(founder, philosopher)
    graph.add_edge(philosopher, founder)
    graph.add_edge(founder, summarizer)
    graph.add_edge(philosopher, summarizer)
    graph.add_edge(summarizer, END)

    # Invoke the graph with an example prompt and show the thinking process
    response = graph.invoke("Tell me how I can live my best life.", show_thinking=True)
    print(response)

if __name__ == "__main__":
    __main__()