# Tool Agent Example

This example demonstrates how to create an agent that can use various tools to help users. The agent is equipped with three sample tools:
1. A calculator that can add numbers
2. A time tool that returns the current time
3. A mock web search tool

## Setup

1. Create a virtual environment (recommended):
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Make sure you have your environment variables set up in a `.env` file:
```
OPENAI_API_KEY=your_api_key_here
```

## Running the Example

To run the example:
```bash
python tool_agent.py
```

This will demonstrate how an agent can use different tools to:
- Perform calculations
- Get the current time
- Search for information (mock implementation)

## Customization

You can modify the example to add your own tools by:
1. Defining new tool functions
2. Adding tool definitions to the `tools` list with:
   - `name`: The name of the tool
   - `description`: What the tool does
   - `parameters`: The parameters the tool accepts
   - `function`: The actual function to call
3. Updating the agent's system prompt to include information about the new tools

## Tool Structure

Each tool is defined as a dictionary with the following structure:
```python
{
    "name": "tool_name",
    "description": "What the tool does",
    "parameters": {
        "param1": {
            "type": "param_type",
            "description": "What this parameter does"
        }
    },
    "function": actual_function
}
```