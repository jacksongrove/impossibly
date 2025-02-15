'''
Graph.py

Initializing the graph structure to define the order in which agents execute and how agents 
communicate with one another.

Author: Jackson Grove
'''
import re
from agent import *
from utils.start_end import START, END
from utils.memory import Memory

class Graph:
    '''
    A directed graph that orchestrates the execution of agents and the flow of communication between them within an agentic architecture.

    This class defines nodes as agents (or special tokens such as START and END) and edges as directional connections that route messages from one node (agent) to another. It manages the order in 
    which agents are invoked, facilitates shared memory access, and extracts routing commands from agent outputs to dynamically control the conversation flow.

    Attributes:
        edges (dict): A mapping where keys are nodes (Agent instances or special tokens) and 
                      values are lists of adjacent nodes representing outgoing connections.
        nodes: A view of the keys of the edges dictionary.

    Methods:
        add_node(agent: Agent | list[Agent]) -> None:
            Adds a node or multiple nodes to the graph. Nodes are not connected until edges are added.
        
        add_edge(node1: Agent | list[Agent], node2: Agent | list[Agent]) -> None:
            Adds directed edges between nodes, routing the output of node1 to the input of node2.
            Self-edges (a node connected to itself) are not allowed.
        
        invoke(user_prompt: str = "", show_thinking: bool = False) -> str:
            Executes the graph workflow, passing the user prompt through the agents until the END node 
            is reached. The method manages shared memory, routes outputs based on agent responses, 
            and returns the final output.
        
        _get_route(node: Agent, output: str):
            Extracts a routing command from an agent's output to determine the next node to invoke. 
            If no valid command is found, a default route is selected.

    Raises:
        ValueError: If an invalid node is referenced (i.e., not added to the graph) during edge addition.
    '''
    def __init__(self) -> None:
        # Initalizing hash map for edges
        self.edges = {
            START: [], 
            END: []
        }
        self.nodes = self.edges.keys()
    

    def add_node(self, agent: Agent | list[Agent]) -> None:
        '''
        Adds a node or multiple nodes to the graph. Nodes will not be connected until edges are added.

        Args:
            agent (Agent or list[Agent]): The Agent object or a list of Agent objects to be added as nodes.

        Raises:
            ValueError: If any item in the provided list is not an Agent.
        '''
        if isinstance(agent, list):
            for a in agent:
                if not isinstance(a, Agent):
                    raise ValueError("All items in the list must be Agent instances.")
                self.edges[a] = []
        elif isinstance(agent, Agent):
            self.edges[agent] = []
        else:
            raise ValueError("agent must be either an Agent or a list of Agents.")
    

    def add_edge(self, node1: Agent | list[Agent], node2: Agent | list[Agent]) -> None:
        '''
        Adds an edge or edges between node1 and node2, routing the output of node1 
        to the input of node2. If either node1 or node2 is a list, an edge is added 
        for every combination of node1 and node2.
        
        Args:
            node1 (Agent or list[Agent]): The node(s) to route from.
            node2 (Agent or list[Agent]): The node(s) to route to.
        '''
        # Normalize node1 to a list if it is not already.
        if not isinstance(node1, list):
            node1 = [node1]
        # Normalize node2 to a list if it is not already.
        if not isinstance(node2, list):
            node2 = [node2]

        # For each combination, add the edge
        for n1 in node1:
            if n1 not in self.edges:
                raise ValueError(f"{n1} is not a valid node in the graph. Please add it first.")
            for n2 in node2:
                if n1 is not n2:
                    if n2 not in self.edges:
                        raise ValueError(f"{n2} is not a valid node in the graph. Please add it first.")
                    self.edges[n1].append(n2)


    def invoke(self, user_prompt: str = "", show_thinking: bool = False) -> str:
        # Output the user prompt if there are no agents defined
        if len(self.nodes) == 2: # (When only START and END nodes are defined)
            return prompt
        
        # Create a global memory for the graph
        global_memory = Memory()

        # Execute each node in the graph until END is reached
        curr_node = self.edges[START][0]
        prompt = user_prompt
        author = 'user'
        while curr_node != END:
            # Check if agent listens to other Agents (has shared memory)
            if curr_node.shared_memory:
                prompt += f'\n\nPrevious messages: \n{global_memory.get_formatted(curr_node.shared_memory, curr_node.shared_memory)}' # TODO: Support distinct author and receiver Agent lists

            # Invoke the current node
            output = curr_node.invoke(author, prompt, self.edges[curr_node], show_thinking)
            # Route to intended node in the case of multiple branching edges
            i = 0
            if len(self.edges[curr_node]) > 1:
                i, output = self._get_route(curr_node, output)

            # Look ahead for the END node, return & display the final output once END is reached
            if self.edges[curr_node][i] == END:
                return output

            # Update global memory
            global_memory.add(curr_node, self.edges[curr_node][i], output)

            # Continue executing through the graph until END is reached
            curr_node = self.edges[curr_node][i]
            prompt = output
            author = 'user'
            
        
    def _get_route(self, node: Agent, output: str):
        '''
        Extracts the desired route from a node's response and returns the index of the corresponding node in the node's edge list. This index is used to determine the next node to invoke. If a 
        command to route to an agent is found, the command is removed from the output. If no command is found, a random route is chosen.
        

        Args:
            :node (Agent): The node to route from
            :output (str): The Agent response to extract the desired route from. The name of the desired agent will be deliminated by a double backslash ('\\').
        '''
        options = self.edges[node]
        # Regex from back of list to find agent names in delimited text
        match = re.search(r'(?<=\\\\)(.*?)(?=\\\\)', output, re.DOTALL)
        if match:
            # Remove the last instance of the command from the output
            output = re.sub(r'\\\\' + re.escape(match.group(1)) + r'\\\\', '', output, count=1)
            
            # Get index of the desired agent in the node's edge list
            # Check if the match is the END command
            if match.group(1) == 'END':
                return options.index(END), output
            else:
                for i, option in enumerate(options):
                    if option.name == match.group(1):
                        return i, output
        print("No route found. Choosing random route.")
        return 0, output