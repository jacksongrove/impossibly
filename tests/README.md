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

To run the tests, first install the package with test dependencies:

```bash
# Install with test dependencies
pip install -e ".[test]"
```

Then run the tests using the CLI command that gets installed with the package:

```bash
# Run all tests
imagination-engine run

# Run just feature tests
imagination-engine run --path features/

# Run tests in Docker
imagination-engine run --docker

# Get help
imagination-engine run --help
```

## CLI Options

### Basic Options

```bash
# Run tests with verbose output
imagination-engine run

# Run tests without verbose output
imagination-engine run --no-verbose

# Run tests with code coverage report
imagination-engine run --cov

# Run tests for a specific test path (relative to tests directory)
imagination-engine run --path features/test_agent_interaction.py

# Run tests matching a specific pattern
imagination-engine run --filter test_conversation

# Just collect tests without running them
imagination-engine run --collect-only
```

### Cleaning Options

```bash
# Clean up pytest cache and temporary files before running tests
imagination-engine run --clean
```

### Docker Options

```bash
# Run tests in Docker
imagination-engine run --docker

# Run tests in Docker and clean up Docker containers and images afterward
imagination-engine run --docker --clean-docker
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