.. Imagination Engine documentation master file, created by
   sphinx-quickstart on Mon May 12 10:55:03 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Imagination Engine
=================

Prototype powerful agentic architectures *impossibly fast*
--------------------------------------------------------------

**Imagination Engine** is a Python framework that empowers you to build, deploy, and orchestrate AI agents in sophisticated graph structures with unprecedented speed and flexibility.

Key capabilities:

* **Lightning-fast prototyping** - Go from concept to working agent graph in minutes, not days
* **Universal LLM support** - Seamlessly switch between providers (OpenAI, Anthropic) with unified interface
* **Flexible agent choreography** - Design directed workflows with our intuitive Graph system
* **Powerful augmentation** - Enhance your agents with RAG, memory sharing, and multi-agent collaboration
* **Real-world integration** - Execute custom Python functions based on agent decisions with our Tools capability
* **Production-ready performance** - Built for both synchronous and asynchronous operations at scale

Getting Started
--------------

.. code-block:: bash

   pip install imagination-engine

For a quick implementation guide, see the :doc:`quickstart`.

.. toctree::
   :maxdepth: 2
   :caption: User Guide
   
   installation
   quickstart
   concepts
   tutorials/index

.. toctree::
   :maxdepth: 2
   :caption: Components
   
   agents
   graphs
   memory
   tools
   rag

.. toctree::
   :maxdepth: 2
   :caption: API Reference
   
   api/agent
   api/graph
   api/utils

.. toctree::
   :maxdepth: 2
   :caption: Development
   
   contributing
   changelog

Indices and tables
=================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

