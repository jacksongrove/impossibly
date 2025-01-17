'''
Graph.py

Initializing the graph structure to define the order in which agents execute and how agents 
communicate with one another.

Author: Jackson Grove 1/15/2025
'''
import os
from dotenv import load_dotenv
from agent import *
from start_end import START, END

class Graph:
    '''
    Graph structure to define the order in which agents execute and how agents communicate with one another.
    '''
    def __init__(self) -> None:
        # Initalizing hash map for edges
        self.edges = {
            START: [], 
            END: []
        }
        self.nodes = self.edges.keys()
    
    def add_node(self, agent: Agent) -> None:
        '''
        Adds a node to the graph. This will not be connected until an edge is added.

        Args:
            :agent (Agent): The Agent object to be added as a node.
        '''
        self.edges[agent] = []
    
    def add_edge(self, node1: Agent, node2: Agent) -> None:
        '''
        Adds an edge from node1 to node2, routing the output of node1 to the input of node2

        Args:
            :node1 (Agent): The node to route from, sending the output to node2's input
            :node2 (Agent): The node to route to, receiving the output of node1 as input
        '''
        self.edges[node1].append(node2)

    def invoke(self, user_prompt: str = "", show_thinking: bool = False) -> str:
        # Output the user prompt if there are no agents defined
        if len(self.nodes) == 2: # (When only START and END nodes are defined)
            return prompt
        
        # Execute each node in the graph until END is reached
        curr_node = self.edges[START][0]
        prompt = user_prompt
        while curr_node != END:
            output = curr_node.invoke(prompt)
            if show_thinking:
                print(f"\n{curr_node.name}:\n {output}\n")
            curr_node = self.edges[curr_node][0] # TODO: add handling for routing/choosing between nodes in the case of multiple edges
            # Return the final output once END is reached
            if curr_node == END:
                return output
            # Otherwise, continue executing through the graph
            prompt = output


def __main__():
    # Load environment variables
    load_dotenv()
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    if not OPENAI_API_KEY:
        raise ValueError("OpenAI API key is not set. Please check your .env file.")

    # Initalize client
    client = OpenAI(api_key=OPENAI_API_KEY)

    # Initalize Agents
    agent1 = Agent(
        client, 
        model= "gpt-4o", 
        name="Agent1", 
        system_prompt="""
            Please rewrite my prompt to be long and detailed, explaining things I may have skimmed over or been brief about. 
            Your goal is to make it as clear as possible for someone else to follow.
            """
    )
    agent2 = Agent(
        client, 
        model= "gpt-4o", 
        name="Agent2", 
        system_prompt="""
            Follow instructions and think critically to solve the problem, writing out your entire thought process to think through each step. 
            Go step by step and do not be afraid to be lengthy in your response — the more meticulous and detailed, the better! 
            Do your thinking first then end with your solution.
            """
    )
    print(agent2.system_prompt)
    agent3 = Agent(
        client, 
        model= "gpt-4o", 
        name="Agent3", 
        system_prompt="""
            You will be given a long thought process taken to solve a problem, reword the answer to just give the solution.
            """
    )

    # Initalize and build Graph
    graph = Graph()

    graph.add_node(agent1)
    graph.add_node(agent2)
    graph.add_node(agent3)

    graph.add_edge(START, agent1)
    graph.add_edge(agent1, agent2)
    graph.add_edge(agent2, agent3)
    graph.add_edge(agent3, END)

    # Invoke graph
    response = graph.invoke("Tell me how I can live my best life.", show_thinking=True)
    print(response)
    

if __name__ == "__main__":
    __main__()