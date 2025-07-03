Installation
============

You can install Impossibly using pip:

.. code-block:: bash

    pip install impossibly

Requirements
------------

Impossibly requires Python 3.9 or later.

Core dependencies:
- ``openai>=1.0.0``: For OpenAI LLMs
- ``anthropic>=0.4.0``: For Anthropic LLMs
- ``python-dotenv>=1.0.0``: For environment variable management
- ``click>=8.0.0``: For CLI commands

Installing from source
----------------------

You can also install the package directly from the source code:

.. code-block:: bash

    git clone https://github.com/jacksongrove/impossibly.git
    cd impossibly
    pip install -e .

Development installation
------------------------

If you're planning to develop or contribute to Impossibly, install the development dependencies:

.. code-block:: bash

    pip install -e ".[dev]"

This will install additional packages for testing, linting, and building the documentation. 