# Impossibly
Impossibly is an agentic orchestration framework for rapidly building agentic architectures in Python. It accelerates agentic development, empowering developers to craft architectures that enable LLMs to excel in higher-order tasks like idea generation and critical thinking.

This library is designed to be used as a backend for AI apps and automations, providing support for all major LLM providers and locally-hosted model endpoints.

# Getting Started
## Installation

Install the base package:
```bash
pip install impossibly
```

Or install with specific integrations:
```bash
# Minimal installations with specific providers
pip install "impossibly[openai]"    # Only OpenAI support
pip install "impossibly[anthropic]" # Only Anthropic support
pip install "impossibly[all]"       # All LLM integrations

# For testing and development
pip install "impossibly[test]"      # All LLM integrations + testing tools
pip install "impossibly[dev]"       # All LLM integrations + testing + dev tools
```

## Imports
Import the components you need:
```python
from impossibly import Agent, Graph, START, END
```

## Setting Up Environment Variables
1. Copy the `.env.template` file to a new file named `.env`:
   ```bash
   cp .env.template .env
   ```

2. Fill in your API keys and configurations in the `.env` file:
   ```
   OPENAI_API_KEY=your_actual_api_key_here
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   ```

3. The library will automatically load these variables when needed. At minimum, you'll need the API key for your preferred LLM provider.

## Initalize Clients for LLM APIs
Done in the format standard to your API.

## Create Agents
Initalize the agents you'd like to call with a simple schema:
```
agent = Agent(
          client=client, 
          model="gpt-4o", 
          name="Agent", 
          system_prompt="You are a friendly assistant.",
          description="This agent is an example agent."
    )
```

## Define how agents are executed with a Graph
Graphs connect agents together using nodes and edges, routing the execution flow and all needed information through the graph. Each node represents an agent and each edge represents a conditional under which that agent is called. This conditional can be defined in natural language for each agent, within its `system_prompt`. 

In the case of multiple edges branching from one node, agents can understand their routing options using the `description` field of connecting nodes.

Every graph accepts user input at the `START` and returns a response to the user at the `END`.

With this basic understanding, a graph can be created in just a few lines.
```
graph = Graph()

graph.add_node(agent)
graph.add_node(summarizer_agent)

graph.add_edge(START, agent)
graph.add_edge(agent, summarizer_agent)
graph.add_edge(summarizer_agent, END)
```

## Run your Graph
You're done! Prompt your agentic architecture.
```
graph.invoke("Hello there!")
```

# Development
## Running Tests

To run the tests, first install the package with test dependencies:

```bash
# Install with test dependencies
pip install -e ".[test]"
```

Then run the tests using the CLI command that gets installed with the package:

```bash
# Run all tests
impossibly run

# Run just feature tests
impossibly run --path features/

# Run tests in Docker
impossibly run --docker

# Get help
impossibly run --help
```

See [tests/README.md](tests/README.md) for more details on the testing framework and available options.

## Local Development and Running Examples

If you want to develop locally and test the examples, follow these steps:

### Building the Package Locally

1. Clone the repository:
   ```bash
   git clone https://github.com/jacksongrove/impossibly.git
   cd impossibly
   ```

2. Create and activate a virtual environment (optional but recommended):
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

4. Build the package locally:
   ```bash
   python -m build
   ```
   This will create distributions in the `dist/` directory.

### Installing the Local Build to Run Examples

There are two approaches to use your local build:

#### Option 1: Install in Development Mode (Recommended)

This allows changes to the source code to be immediately reflected without reinstalling:

```bash
pip install -e .
```

#### Option 2: Install the Built Wheel

If you want to test the exact distribution that would be uploaded to PyPI:

```bash
pip install dist/impossibly-0.1.0-py3-none-any.whl
```

### Running Examples

Once you've installed the package using either method, you can run the examples:

```bash
# Set up your environment variables first
cp .env.template .env
# Edit .env to add your API keys

# Run an example
python examples/image_agent/image_agent.py

# Or try another example
python examples/web_search_agent/web_search_agent.py
```

Make sure the required dependencies for each example are installed and the necessary API keys are in your `.env` file.
