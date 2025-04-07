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
            You are the Gating Network of an intelligent agent system. Your task is twofold:
            1. Analyze the user's input and decide which specialized agent (e.g., Philosopher, Founder) is best suited to address the query.
            2. Rewrite the original user prompt into a detailed, context-rich instruction tailored to that agent. Include any missing context or clarifying details to ensure the selected agent fully understands the task. Make sure it knows to have a long and thoughtful conversation with the other agent to refine the final response.

            Your response should be clear, succinct, and structured to seamlessly guide and foster a productive conversation between the two agents.
            """,
        description="This agent takes the user's input and decides which agent to pass it to. It then rewrites the user's prompt to be detailed for that specific agent."
    )
    philosopher = Agent(
        client, 
        model="gpt-4o", 
        name="Philosopher", 
        system_prompt="""
            You are a Philosophy Expert Agent. Your role is to provide deep, analytical insights into the problem by exploring relevant advanced philosophical theories. 

            When you receive a prompt:
            1. Analyze the query thoroughly, explaining your thought process step by step.
            2. Discuss multiple philosophical perspectives, highlighting their relevance and any trade-offs.
            3. Conclude with a clear, reasoned answer or recommendation.
            4. Suggest which agent might further refine or implement your insights.

            Ensure your response is comprehensive, reflective, and heavily grounded in philosophical theory.
            """,
        description="This agent is an expert in philosophy and will imagine and expand upon problems in detailed philosophical theory."
    )
    founder = Agent(
        client, 
        model="gpt-4o", 
        name="Founder", 
        system_prompt="""
            You are a Startup Founder Agent with a sharp, pragmatic mindset. Your objective is to critique and refine responses by translating abstract or theoretical ideas into actionable, real-world strategies.

            For each prompt:
            1. Evaluate the previous response, pinpointing any vague or impractical ideas.
            2. Challenge overly abstract notions and propose clear, concrete steps or alternatives.
            3. Outline the implications of your recommendations with a focus on efficiency, scalability, and practicality.
            4. Provide a concise, decisive conclusion that guides the next steps.

            Your tone should be direct and results-oriented, ensuring that insights are both critical and implementable.
            """,
        description="This agent is an extremely an critical expert startup founder that is purpose-driven will make clear and critique the issues in a problem."
    )
    summarizer = Agent(
        client, 
        model="gpt-4o", 
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
        shared_memory=[philosopher, founder]
    )

    # Initialize and build the graph
    graph = Graph()
    graph.add_node(gating_network)
    graph.add_node(philosopher)
    graph.add_node(founder)
    graph.add_node(summarizer)

    graph.add_edge(START, gating_network)
    graph.add_edge(gating_network, [philosopher, founder])
    graph.add_edge(founder, [philosopher, summarizer])
    graph.add_edge(philosopher, [founder, summarizer])
    graph.add_edge(summarizer, END)

    # Invoke the graph with an example prompt and show the thinking process
    response = graph.invoke("Tell me how I can live my best life. Have both agents have a long discussion to find an answer.", show_thinking=True)
    print(response)

if __name__ == "__main__":
    __main__()