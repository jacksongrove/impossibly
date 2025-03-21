# Image Agent Example

This example demonstrates how to create and use an image analysis agent using the Imagination Engine. The agent can analyze images and provide descriptions or answer questions about their contents.

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

4. Place your image file:
   - Put your image file (e.g., `image_input.jpeg`) in the `image_agent` directory
   - The default image path is set to `image_input.jpeg` in the current directory

## Running the Example

To run the example:
```bash
python image_agent.py
```

This will demonstrate how an agent can analyze an image and provide insights about its contents. The example uses GPT-4 Vision to process the image and answer questions about it.

## Customization

You can modify the example to analyze different images by:
1. Changing the image file path in the script
2. Modifying the prompt to ask different questions about the image
3. Adjusting the agent's system prompt to specialize in different types of image analysis 