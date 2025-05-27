Installation
============

You can install Imagination Engine using pip:

.. code-block:: bash

    pip install imagination-engine

Requirements
-----------

Imagination Engine requires Python 3.9 or later.

Core dependencies:
- ``openai>=1.0.0``: For OpenAI LLMs
- ``anthropic>=0.4.0``: For Anthropic LLMs
- ``python-dotenv>=1.0.0``: For environment variable management
- ``click>=8.0.0``: For CLI commands

Installing from source
---------------------

You can also install the package directly from the source code:

.. code-block:: bash

    git clone https://github.com/jacksongrove/imagination-engine.git
    cd imagination-engine
    pip install -e .

Development installation
-----------------------

If you're planning to develop or contribute to Imagination Engine, install the development dependencies:

.. code-block:: bash

    pip install -e ".[dev]"

This will install additional packages for testing, linting, and building the documentation. 