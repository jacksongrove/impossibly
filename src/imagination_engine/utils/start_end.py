'''
Defining nodes to signify the start and end of a graph
'''

class START_node:
    '''
    Node to signify the start of the graph (initial user input).
    Implemented as a singleton.
    '''
    def __str__(self) -> str:
        return "START"


class END_node:
    '''
    Node to signify the end of the graph (final output).
    Implemented as a singleton.
    '''
    def __str__(self) -> str:
        return "END"
    
    
# Instantiate singleton objects
START = START_node()
END = END_node()