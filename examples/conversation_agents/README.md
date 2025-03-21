# Conversation Agents Example

This example demonstrates how to create and run conversation agents using the Imagination Engine.

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
python conversation_agents.py
```

This will demonstrate a conversation between multiple agents, showing how they can interact and maintain context throughout the conversation. 