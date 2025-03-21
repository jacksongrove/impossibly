# Tool Agent Example

This example demonstrates how an agent can utilize various tools to perform actions and process information.

## Setup

1. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up your environment variables in a .env file:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

4. Run the example:
   ```
   python tool_agent.py
   ```

## Customization

You can customize this example by adding your own tools. To create a new tool, you need to:

1. Define a function that implements the tool's functionality
2. Create a Tool object with the function and its parameters
3. Add the tool to the agent

### Creating Tools

The `Tool` class provides a simple and lightweight way to define tools:

```python
from utils.tools import Tool

# Define a function that implements the tool
def my_tool_function(param1, param2=0.0):
    """Tool function implementation"""
    return f"Result of processing {param1} and {param2}"

# Create a tool with Python types
my_tool = Tool(
    name="my_tool",
    description="Description of what my tool does",
    function=my_tool_function,
    parameters=[
        {
            "name": "param1",
            "type": str,  # Python string type
            "description": "First parameter description"
        },
        {
            "name": "param2",
            "type": float,  # Python float type
            "description": "Second parameter description",
            "required": False  # Optional parameter
        }
    ]
)
```

### Supported Parameter Types

The system supports the following Python types directly:

- `str`: For text values
- `int`: For integer values
- `float`: For floating-point numbers
- `bool`: For boolean values
- `list`: For arrays
- `dict`: For objects/maps

### Adding Tools to an Agent

Once you've created your tools, add them to an agent:

```python
agent = Agent(
    client,
    model="gpt-4o",
    name="MyToolAgent",
    system_prompt="You are an agent that can use various tools...",
    description="A helpful agent with tools",
    tools=[my_tool, another_tool]
)
```

The agent will automatically format the tools for the API and handle tool execution.