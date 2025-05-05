import os
from dotenv import load_dotenv
from imagination_engine import Agent, Graph, START, END

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
    agent1 = Agent(
        client, 
        model="gpt-4o", 
        name="Agent1", 
        system_prompt="""
            You are an agent within an agentic architecture. You will get input from the user but have to output it in terms another agent understands. 
            Please rewrite my prompt to be long and detailed, explaining things I may have skimmed over or been brief about. 
            Your goal is to make it as clear as possible for someone else to follow.
            """,
        description="This agent takes the user's input and rewrites it to be more detailed and clear for another agent to understand."
    )
    agent2 = Agent(
        client, 
        model="gpt-4o", 
        name="Agent2", 
        system_prompt="""
            You are an agent within an agentic architecture. You will get input from another agent and have to output it in terms a different agent understands.
            Follow instructions and think critically to solve the problem, writing out your entire thought process to think through each step. 
            Go step by step and do not be afraid to be lengthy in your response — the more meticulous and detailed, the better! 
            Do your thinking first then end with your solution.
            """,
        description="This agent takes the detailed input from the first agent and thinks through the problem step by step, explaining the entire thought process."
    )
    agent3 = Agent(
        client, 
        model="gpt-4o", 
        name="Agent3", 
        system_prompt="""
            You are an agent within an agentic architecture. You will get input from another agent and have to output it in terms a different agent understands.
            No matter your input, reword the answer to be brief and just give the solution in one line.
            """,
        description="This agent takes the detailed thought process from the second agent and outputs a brief solution."
    )

    # Initialize and build the graph
    graph = Graph()
    graph.add_node(agent1)
    graph.add_node(agent2)
    graph.add_node(agent3)

    graph.add_edge(START, agent1)
    graph.add_edge(agent1, agent2)
    graph.add_edge(agent2, agent3)
    graph.add_edge(agent3, END)

    # Invoke the graph with an example prompt and show the thinking process
    response = graph.invoke("Tell me how I can live my best life.", show_thinking=True)
    print(response)

if __name__ == "__main__":
    __main__()