# Imagination Engine Tests

This directory contains various tests for the Imagination Engine library, organized by test type and purpose.

## Test Structure

The test suite is organized into the following directories:

- **Unit Tests**: (`tests/unit/`) - Tests for individual components in isolation
- **Integration Tests**: (`tests/integration/`) - Tests for combinations of components working together
- **Feature Tests**: (`tests/features/`) - Tests focused on verifying specific features of the framework

## Running Tests

### Running All Tests

To run all tests in the suite:

```bash
pytest tests/
```

### Running Specific Test Types

To run just unit tests:

```bash
pytest tests/unit/
```

To run just integration tests:

```bash
pytest tests/integration/
```

To run just feature tests:

```bash
pytest tests/features/
```

### Running Specific Test Files

To run tests from a specific file:

```bash
pytest tests/unit/test_agent.py
```

### Running Specific Test Cases

To run a specific test case by name:

```bash
pytest tests/unit/test_agent.py::TestAgentBasics::test_agent_initialization_with_anthropic
```

## Integration Test Script

The repository includes a bash script to run and evaluate all example scripts:

```bash
tests/integration/run_examples.sh
```

This script:
1. Runs all example scripts in parallel with a 60-second timeout
2. Captures the output and exit code of each example
3. Categorizes examples as succeeded, failed, or timed out
4. Provides a detailed summary of results

## Test Configuration

Common fixtures and test configurations are defined in `tests/conftest.py`. These fixtures are automatically available to all test modules and provide:

- Mock LLM clients (OpenAI and Anthropic)
- Basic tools for testing
- Other shared resources

## Adding New Tests

When adding new tests:

1. Place unit tests in the `tests/unit/` directory
2. Place integration tests in the `tests/integration/` directory
3. Place feature-focused tests in the `tests/features/` directory
4. Use the shared fixtures from `conftest.py` where possible
5. Follow the existing naming conventions (`test_*.py` for files, `TestClassName` for classes, `test_method_name` for methods)

## Test Mocking

Tests use the `unittest.mock` module to mock external dependencies, particularly:

- LLM API calls to OpenAI and Anthropic
- File system operations
- External tool dependencies

This allows tests to run without actual API keys or external services. 