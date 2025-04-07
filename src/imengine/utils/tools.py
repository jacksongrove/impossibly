'''
Utility module for managing tools in the Imagination Engine.

This module provides a Tool class for defining and formatting tools
for use with various language model APIs (OpenAI, Anthropic, etc.).
'''

import asyncio

# Type mapping from Python types to OpenAI API types
TYPE_MAPPING = {
    str: "string",
    int: "integer",
    float: "number",
    bool: "boolean",
    list: "array",
    dict: "object",
}

class Tool:
    """
    Represents a tool that can be used by an agent.
    
    This class handles the definition and formatting of tools for various API providers.
    """
    def __init__(self, name, description, function, parameters=None):
        """
        Initialize a tool with its metadata and function.
        
        Args:
            name: The name of the tool
            description: A description of what the tool does
            function: The function to execute when the tool is called
            parameters: List of parameter definitions (dicts with name, type, description)
        """
        self.name = name
        self.description = description
        self.function = function
        self.parameters = []
        
        # Check if the function is a coroutine function
        self.is_async = asyncio.iscoroutinefunction(function)
        
        # Process parameters
        if parameters:
            for param in parameters:
                # Convert param dict to full param dict with API type
                if isinstance(param, dict):
                    param_type = param["type"]
                    if param_type not in TYPE_MAPPING:
                        valid_types = ", ".join(t.__name__ for t in TYPE_MAPPING)
                        raise ValueError(f"Unsupported type: {param_type}. Use one of: {valid_types}")
                    
                    self.parameters.append({
                        "name": param["name"],
                        "type": param_type,
                        "api_type": TYPE_MAPPING[param_type],
                        "description": param["description"],
                        "required": param.get("required", True)
                    })
                else:
                    # Already processed param, just add it
                    self.parameters.append(param)
        
        # Pre-format for OpenAI
        self._formatted_tool = self._format_for_openai()
    
    def _format_for_openai(self):
        """Format the tool for OpenAI's API."""
        formatted_tool = {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        }

        for param in self.parameters:
            formatted_tool["function"]["parameters"]["properties"][param["name"]] = {
                "type": param["api_type"],
                "description": param["description"]
            }
            if param.get("required", True):
                formatted_tool["function"]["parameters"]["required"].append(param["name"])

        return formatted_tool

    def format_for_api(self, api="openai"):
        """
        Format the tool for a specific API.
        
        Args:
            api: The API to format for ("openai" or "anthropic")
            
        Returns:
            Dict containing the formatted tool definition
        """
        if api == "openai":
            return self._formatted_tool
        elif api == "anthropic":
            # TODO: Implement Anthropic formatting when needed
            raise NotImplementedError("Anthropic tool formatting not yet implemented")
        else:
            raise ValueError(f"Unsupported API: {api}")

    def execute(self, **kwargs):
        """
        Execute the tool's function with the given arguments.
        
        This method detects if it's being called from an async context and acts accordingly.
        If called from sync code, it runs the async implementation using asyncio.run().
        If called from async code, it returns a coroutine that can be awaited.
        """
        if self.is_async:
            try:
                # Check if we're in an event loop
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # We're being called from an async context
                    # Return the coroutine for the caller to await
                    return self._execute_async(**kwargs)
                else:
                    # No running event loop, create one
                    result = asyncio.run(self._execute_async(**kwargs))
                    return result
            except RuntimeError as e:
                # No event loop exists, create one
                result = asyncio.run(self._execute_async(**kwargs))
                return result
            except Exception as e:
                raise
        else:
            # Function is synchronous, just call it directly
            try:
                result = self.function(**kwargs)
                return result
            except Exception as e:
                raise
    
    async def _execute_async(self, **kwargs):
        """Internal async implementation of execute for async functions."""
        return await self.function(**kwargs)


def format_tools_for_api(tools, api="openai"):
    """Format a list of tools for a specific API."""
    return [tool.format_for_api(api) for tool in tools] 