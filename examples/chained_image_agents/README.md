# Chained Image Agents Example

This example demonstrates how to create a chain of image generation agents that can work together to create complex images.

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
python chained_image_agents.py
```

This will demonstrate how multiple image generation agents can work together in a chain, with each agent building upon the work of the previous one. 