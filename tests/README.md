# Imagination Engine Tests

This directory contains various tests for the Imagination Engine library, organized by test purpose.

## Test Structure

The test suite is organized into the following directories:

- **Feature Tests**: (`tests/features/`) - Tests focused on verifying specific features of the framework, including:
  - Agent interaction and communication
  - Tool functionality and usage
  - Image handling capabilities
- **Utils**: (`tests/utils/`) - Utility functions and classes to support testing, such as mock clients
- **Scripts**: (`tests/scripts/`) - Testing scripts and Docker configuration files

## Setup and Dependencies

Install the package with test dependencies using the "extras" feature in setup.py:

```bash
# Install the package with test dependencies
pip install -e ".[test]"
```

The `[test]` extras include:
- All LLM client libraries (OpenAI, Anthropic)
- Testing framework (pytest and pytest-cov)
- Mocking utilities (mock)

For development with additional tools (black, flake8, etc.):
```bash
pip install -e ".[dev]"
```

## Running Tests

### Using the CLI Command

The most elegant way to run tests is to use the provided CLI command, which gets installed with the package:

```bash
# Run all tests
imengine-test run

# Run specific feature tests
imengine-test run --path features/

# Run tests in Docker
imengine-test run --docker

# Get help
imengine-test run --help
```

This Python-based command works from any directory and avoids the need for shell scripts.

### Using pytest Directly

You can also run pytest directly:

```bash
# Run all tests
python -m pytest tests/

# Run feature tests only
python -m pytest tests/features/

# Run a specific test file
python -m pytest tests/features/test_agent_interaction.py

# Run a specific test case
python -m pytest tests/features/test_agent_interaction.py::TestAgentInteraction::test_conversation_memory
```

### Verifying Test Discovery

To check which tests will be run without actually running them:

```bash
# Using the CLI command
imengine-test run --collect-only

# Using pytest directly
python -m pytest tests/ --collect-only -v
```

## Docker Testing

You can run tests in Docker using the CLI command:

```bash
# Run tests in Docker
imengine-test run --docker

# Clean up Docker resources
imengine-test run --docker --clean-docker
```

## Test Configuration

Common fixtures and test configurations are defined in `tests/conftest.py`. These fixtures are automatically available to all test modules and provide:

- Mock LLM clients (OpenAI and Anthropic)
- Basic tools for testing
- Other shared resources

## Test Mocking

Tests use the `unittest.mock` module to mock external dependencies, particularly:

- LLM API calls to OpenAI and Anthropic
- File system operations
- External tool dependencies

This allows tests to run without actual API keys or external services.

## Troubleshooting

If you encounter issues running the tests:

1. **Module not found errors**: Ensure you've installed the package with test dependencies (`pip install -e ".[test]"`)
2. **Script execution errors**: Make sure the package is properly installed with the CLI command
3. **Docker issues**: Check that Docker and Docker Compose are installed and running
4. **Test discovery issues**: Verify that your test files follow the naming convention `test_*.py`

## Adding New Tests

When adding new tests:

1. Place feature-focused tests in the `tests/features/` directory
2. Add testing utilities to the `tests/utils/` directory
3. Use the shared fixtures from `conftest.py` where possible
4. Follow the existing naming conventions (`test_*.py` for files, `TestClassName` for classes, `test_method_name` for methods)

### Current Feature Test Files

- `test_agent_interaction.py`: Tests agent creation, communication, memory, and multi-agent collaboration
- `test_tools.py`: Tests tool definition, execution, parameter validation, and agent integration with tools
- `test_image_capabilities.py`: Tests image handling, multimodal inputs, and vision-based agent functionality 