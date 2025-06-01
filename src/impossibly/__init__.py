# This file can be empty or used for package-level initialization. 

"""
Impossibly - Modular, extensible agent framework for building multi-agent systems.

Key components can be imported directly from impossibly:
    from impossibly import Agent, Graph
    # or
    import impossibly
    agent = impossibly.Agent(...)
"""

# Core components
from .agent import Agent, OpenAIAgent, AnthropicAgent
from .graph import Graph

# Utility components
from .utils.memory import Memory
from .utils.tools import Tool, format_tools_for_api
from .utils.start_end import START, END

# For backward compatibility
__all__ = [
    'Agent', 'OpenAIAgent', 'AnthropicAgent',
    'Graph',
    'Memory',
    'Tool', 'format_tools_for_api',
    'START', 'END'
]