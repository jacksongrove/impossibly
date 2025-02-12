'''
Graph.py

Initializing the graph structure to define the order in which agents execute and how agents 
communicate with one another.

Author: Jackson Grove
'''
import re
from agent import *
from utils.start_end import START, END

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
        author = 'user'
        while curr_node != END:
            output = curr_node.invoke(author, prompt, self.edges[curr_node], show_thinking)
            # Route to intended node in the case of multiple branching edges
            i = 0
            if len(self.edges[curr_node]) > 1:
                i, output = self._get_route(curr_node, output)
            curr_node = self.edges[curr_node][i]

            # Return the final output once END is reached
            if curr_node == END:
                return output
            # Otherwise, continue executing through the graph
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