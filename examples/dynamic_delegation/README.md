# Dynamic Delegation Architecture

This example demonstrates an advanced agentic architecture that implements dynamic delegation for problem-solving. It features an executive-level agent that can either answer simple queries directly or delegate complex tasks to specialized teams of experts, adapting its response strategy based on query complexity.

## Overview

The architecture implements a context-aware, hierarchical decision-making process:

1. An Executive Agent analyzes user queries and determines their complexity
2. For simple queries, it responds directly, optimizing resource usage
3. For complex queries, it dynamically creates a specialized team of experts by:
   - Selecting the appropriate expert types for the problem
   - Dynamically building a new agent graph
   - Delegating the work to this expert team
   - Synthesizing the team's findings into a comprehensive response

This demonstrates how agents can optimize resource allocation through contextual decision-making and hierarchical collaboration, similar to how human organizations efficiently handle tasks of varying complexity.

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
python dynamic_delegation.py
```

The script demonstrates two example queries:
1. A simple query ("What is the capital of France?") that gets answered directly
2. A complex query about climate change that triggers the creation of an expert team

## Customization

You can customize this example in several ways:

### Adding New Expert Types

Add new expert types to the `expert_definitions` dictionary in the `create_expert_team` function:

```python
expert_definitions = {
    "new_expert_type": {
        "name": "NewExpert",
        "system_prompt": """
            System prompt for the new expert...
        """,
        "description": "Description of the new expert's capabilities"
    },
    # ...existing expert definitions...
}
```

### Modifying the Executive Agent Logic

You can change how the executive agent decides when to delegate by modifying its system prompt:

```python
executive_agent = Agent(
    client, 
    model="gpt-4o", 
    name="ExecutiveAgent", 
    system_prompt="""
        Your custom logic for when to delegate vs. answer directly...
    """,
    # ...rest of agent definition...
)
```

### Changing Team Structure

Modify the graph structure in the `create_expert_team` function to implement different team collaboration patterns:

```python
# Example: Adding peer-to-peer collaboration between experts
for expert1 in expert_agents:
    for expert2 in expert_agents:
        if expert1 is not expert2:
            team_graph.add_edge(expert1, expert2)
```
