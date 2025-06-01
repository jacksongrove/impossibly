'''
Graph.py

Initializing the graph structure to define the order in which agents execute and how agents 
communicate with one another.

Author: Jackson Grove
'''
import re
import asyncio
import os
from typing import Union, List, Tuple
from impossibly.agent import *
from impossibly.utils.start_end import START, END
from impossibly.utils.memory import Memory

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
        add_node(agent: Union[Agent, List[Agent]]) -> None:
            Adds a node or multiple nodes to the graph. Nodes are not connected until edges are added.
        
        add_edge(node1: Union[Agent, List[Agent]], node2: Union[Agent, List[Agent]]) -> None:
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
    

    def add_node(self, agent: Union[Agent, List[Agent]]) -> None:
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
    

    def add_edge(self, node1: Union[Agent, List[Agent]], node2: Union[Agent, List[Agent]]) -> None:
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


    def invoke(self, user_prompt: str = "", files: list[str] = [], show_thinking: bool = False) -> str:
        """
        Public method that transparently handles both sync and async execution.
        
        This method detects if it's being called from an async context and acts accordingly.
        If called from sync code, it runs the async implementation using asyncio.run().
        If called from async code, it returns a coroutine that can be awaited.
        
        This provides a unified API that works for both sync and async callers.
        """
        try:
            # Check if we're in an event loop
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # We're being called from an async context
                # Return the coroutine for the caller to await
                return self._invoke_async(user_prompt, files, show_thinking)
            else:
                # No running event loop, create one
                return asyncio.run(self._invoke_async(user_prompt, files, show_thinking))
        except RuntimeError:
            # No event loop exists, create one
            return asyncio.run(self._invoke_async(user_prompt, files, show_thinking))


    async def _invoke_async(self, user_prompt: str = "", files: list[str] = [], show_thinking: bool = False) -> str:
        """Internal async implementation of the invoke method."""
        # Output the user prompt if there are no agents defined
        if len(self.nodes) == 2: # (When only START and END nodes are defined)
            return user_prompt
        
        # Create a global memory for the graph
        global_memory = Memory()

        # Execute each node in the graph until END is reached
        curr_node = self.edges[START][0]
        prompt = user_prompt
        author = 'user'
        selected_files = files
        while curr_node != END:
            # Check if agent listens to other Agents (has shared memory)
            if curr_node.shared_memory:
                prompt += f'\n\nPrevious messages: \n{await global_memory.get_formatted(curr_node.shared_memory, curr_node.shared_memory)}'

            # Invoke the current node
            output = await curr_node.invoke(author, prompt, selected_files, self.edges[curr_node], show_thinking)
            
            # Route to intended node in the case of multiple branching edges
            i = 0
            if len(self.edges[curr_node]) > 1:
                route_idx, output = self._get_route(curr_node, output)
            
            # Route files intended to be passed
            selected_files, output = self._get_files(files, output)

            # Look ahead for the END node, return & display the final output once END is reached
            if self.edges[curr_node][i] == END:
                return output

            # Update global memory
            await global_memory.add(curr_node, self.edges[curr_node][i], output)

            # Continue executing through the graph until END is reached
            curr_node = self.edges[curr_node][i]
            prompt = output
            author = 'user'
        
        return None
    
    def _get_route(self, node: Agent, output: str) -> tuple[int, str]:
        '''
        Extracts the desired routing command from a node's response and returns the index of the corresponding 
        node in the node's edge list. The routing command is expected to be delimited by double backslashes (\\).
        If a routing command is found, it is removed from the output. If the command is "END", the index corresponding
        to the END command is returned. Otherwise, the function searches for an agent whose name matches the command.
        If no valid routing command is found, a default route (index 0) is chosen.
        
        Args:
            node (Agent): The node from which the routing command is being extracted. Its edge list contains the available routing options.
            output (str): The agent's response that contains the routing command. The desired agent name should be delimited by double backslashes (e.g., '\\AgentName\\').
        
        Returns:
            tuple: A tuple containing:
                - int: The index of the chosen route in the node's edge list.
                - str: The output string with the routing command removed.
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


    def _get_files(self, file_options: list[str], output: str) -> tuple[list[str], str]:
        '''
        Extracts all file command options from the agent's output and returns a list of file paths 
        corresponding to the matched file options in the provided file_options list. The file commands 
        are expected to be delimited by <<FILE>> and <</FILE>>. After extraction, all file command blocks 
        are removed from the output. Only files that exist on the filesystem are returned.
        
        Args:
            file_options (List[str]): A list of valid file paths that can be passed to the next agent.
            output (str): The agent's response containing one or more file commands, each delimited by 
                        <<FILE>> and <</FILE>>.
            
        Returns:
            Tuple[List[str], str]: A tuple containing:
                - A list of file paths (from file_options) that exist on the filesystem and were specified 
                in the output.
                - The output string with all file command blocks removed.
        '''
        # Precompute a mapping from option (trimmed) to its file path for O(1) lookups
        option_to_file = {option.strip(): option for option in file_options}

        # Find all file command matches (allowing multiple matches)
        matches = re.findall(r'<<FILE>>(.*?)<</FILE>>', output, re.DOTALL)
        valid_chosen_files = []

        for match in matches:
            option = match.strip()
            if option in option_to_file:
                file_path = option_to_file[option]
                # Check if the file exists
                if os.path.isfile(file_path):
                    print("FILE SENT TO NEXT AGENT:     "+file_path)
                    valid_chosen_files.append(file_path)
                else:
                    print(f"File '{file_path}' does not exist. Ignoring.")
            else:
                print(f"File option '{option}' not found in file_options.")
        
        # Clean the output of all file command blocks.
        output = re.sub(r'<<FILE>>.*?<</FILE>>', '', output, flags=re.DOTALL)
        
        return valid_chosen_files, output