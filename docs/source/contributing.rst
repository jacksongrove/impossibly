Contributing
============

Thank you for your interest in contributing to Imagination Engine! This guide will help you get started with the development process.

Development Environment
---------------------

First, clone the repository and set up a development environment:

.. code-block:: bash

    git clone https://github.com/jacksongrove/imagination-engine.git
    cd imagination-engine
    pip install -e ".[dev]"

This will install the package in development mode with all the development dependencies.

Code Style
---------

We use the following tools to maintain code quality:

- **Black**: For consistent code formatting
- **Flake8**: For code linting
- **isort**: For import sorting
- **mypy**: For type checking

You can run these tools with:

.. code-block:: bash

    black src tests
    flake8 src tests
    isort src tests
    mypy src

Alternatively, you can set up pre-commit hooks to run these automatically before each commit.

Testing
------

We use pytest for testing. To run the tests:

.. code-block:: bash

    pytest

To run tests with coverage:

.. code-block:: bash

    pytest --cov=imagination_engine

Pull Request Process
------------------

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Make your changes
4. Run the tests to ensure they pass
5. Update the documentation if needed
6. Push to your fork and submit a pull request

When submitting a pull request, please include:

- A clear description of the changes
- Any relevant issue numbers (e.g., "Fixes #123")
- Updates to documentation if applicable

Documentation
-----------

Please update the documentation for any new features or changes. We use Sphinx for documentation. To build the docs:

.. code-block:: bash

    cd docs
    make html

The documentation will be generated in `docs/build/html`.

Writing Good Docstrings
----------------------

We use Google-style docstrings. Here's an example:

.. code-block:: python

    def example_function(param1, param2):
        """Short description of the function.
        
        More detailed description of the function and its behavior.
        
        Args:
            param1 (type): Description of param1
            param2 (type): Description of param2
            
        Returns:
            type: Description of return value
            
        Raises:
            ExceptionType: When and why this exception is raised
            
        Example:
            >>> example_function(1, 2)
            3
        """
        # Function implementation here 