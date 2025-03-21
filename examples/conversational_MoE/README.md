# Conversational Mixture of Experts Example

This example demonstrates how to implement a conversational Mixture of Experts (MoE) architecture using the Imagination Engine, where different specialized agents work together to engage in complex conversations.

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
python conversational_MoE.py
```

This will demonstrate how multiple specialized agents can work together in a conversational Mixture of Experts architecture, with each agent contributing their expertise to engage in complex discussions and problem-solving. 