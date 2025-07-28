<div align="center">
  <img src="impossibly.png" alt="Impossibly Logo" width="600">
  
  <p><strong>Build, orchestrate and scale agents impossibly fast</strong></p>
  
  [![PyPI version](https://badge.fury.io/py/impossibly.svg)](https://badge.fury.io/py/impossibly)
  [![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
  [![GitHub stars](https://img.shields.io/badge/github-stars-yellow?style=social&logo=github)](https://github.com/jacksongrove/impossibly)
  [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
  [![Documentation](https://img.shields.io/badge/docs-impossibly.dev-blue)](https://impossibly.dev)
  
  [**Documentation**](https://impossibly.dev) | [**Examples**](examples/) | [**Discord**](https://discord.gg/impossibly) | [**GitHub**](https://github.com/jacksongrove/impossibly)
</div>

---

# Impossibly

Impossibly is a lean Python library for building and orchestrating production AI agents. Declare tools as plain Python functions, keep a tiny dependency footprint, and skip the boilerplate—the stable core ships with first-class multimodal support and built-in tracing so you can ship and debug impossibly fast.

🎯 Why Impossibly?
---
1. Stable core without surprise breakages.
2. Ultra-lean footprint. No dependency bloat.
3. Declare tools as plain Python functions.
4. Multi-modal out of the box.
5. Powerful agents without the boilerplate. It's time to build impossibly fast.

## 🚀 Quick Start

```python
from impossibly import Agent, Graph, START, END

# Create an Impossibly agent
agent = Agent(
    client=openai_client,
    model="gpt-4o",
    system_prompt="You are a helpful assistant",
    tools=[web_search, calculator, database]
)

# Build a reasoning workflow
graph = Graph()
graph.add_edge(START, agent)
graph.add_edge(agent, END)

# Execute with autonomous reasoning
result = graph.invoke("Analyze current market trends and provide strategic recommendations")
```

## ✨ Core Features

### One-line Agent Instantiation
Define agents and the tools available to them in a single object instantiation:
- **Native Multi-modal Support**: Agents can work with both text and images straight out of the box
- **Native Routing**: Under-the-hood prompt-injection to ensure intelligent decision making and routing
- **Custom Functions:**
Build functions simply with Python, then connect them as tools to your agents

### Graph-Based Orchestration
Agents connected with a visual and intuitive workflow design:
- **Conditional Logic**: Route based on agent decisions
- **Monitoring**: Track agent performance and decisions

### Tool Integration
Seamless connection to external systems and data with native Python functions:
- **User-Created Tools**: Connect to any API, service, database and more with self-defined Python functions
- **Own Your Tools**: Core updates won't break your functions—full control and easy fixes
- **Custom Tools**: Build domain-specific capabilities with Python

### Designed for Multi-Agent Architectures
Specialized agents working together on complex tasks:
- **Role-Based Design**: Each agent has a specific expertise
- **Coordinated Workflows**: Agents pass work between each other
- **Quality Assurance**: Multiple agents validate and improve results
- **Scalable Architecture**: Add agents as complexity grows

## 📚 Examples

Explore practical implementations in the `/examples` directory:

- **SQL Agent**: Autonomous database analysis with iterative reasoning
- **Research Agent**: Multi-step research with source validation
- **Conversational Agents**: Context-aware dialogue systems
- **Tool Agents**: Specialized agents for specific tasks
- **Mixture of Experts**: Dynamic agent selection based on task requirements

## 🛠 Installation

```bash
# Base installation
pip install impossibly

# With specific LLM providers only
pip install "impossibly[openai]"
pip install "impossibly[anthropic]"
pip install "impossibly[all]"

# For development & contributions
pip install "impossibly[dev]"
```

## 🧪 Testing

```bash
# Install with test dependencies
pip install -e ".[test]"

# Run test suite
impossibly run

# Run in Docker
impossibly run --docker
```

## 📖 Documentation

Visit **[impossibly.dev](https://impossibly.dev)** for:
- Complete API documentation
- Agentic AI tutorials and guides
- Framework comparisons (LangGraph, CrewAI, AutoGen)
- Real-world case studies
- Best practices for building reliable agents

## 🤝 Community

- **Discord**: [Join our community](https://discord.gg/impossibly)
- **GitHub**: [Contribute to the project](https://github.com/jacksongrove/impossibly)
- **Documentation**: [Learn more at impossibly.dev](https://impossibly.dev)

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

**Ready to build, orchestrate and scale AI agents impossibly fast?** Start with the [documentation](https://impossibly.dev) and join the community pushing the boundaries of autonomous AI.
