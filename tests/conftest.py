"""
Shared fixtures for all test modules.

This file contains fixtures that can be used across all test modules,
reducing duplication and ensuring consistent test setup.
"""
import pytest
from unittest.mock import MagicMock, patch

# Import the utility functions
from .utils.client_mocks import create_mock_anthropic, create_mock_openai
from impossibly import Tool


@pytest.fixture
def mock_anthropic_client():
    """Create a mock Anthropic client for testing."""
    with patch("anthropic.Anthropic") as mock_client_class:
        # Create a properly structured mock that will pass isinstance checks
        mock_client = create_mock_anthropic()
        mock_client_class.return_value = mock_client
        
        yield mock_client


@pytest.fixture
def mock_openai_client():
    """Create a mock OpenAI client for testing."""
    with patch("openai.OpenAI") as mock_client_class:
        # Create a properly structured mock that will pass isinstance checks
        mock_client = create_mock_openai()
        mock_client_class.return_value = mock_client
        
        yield mock_client


@pytest.fixture
def mock_clients(mock_anthropic_client, mock_openai_client):
    """Create both OpenAI and Anthropic clients for testing multi-model scenarios."""
    return (mock_anthropic_client, mock_openai_client)


@pytest.fixture
def basic_tools():
    """Create a set of basic tools for testing."""
    # Simple calculator tool
    def add_numbers(a, b):
        return a + b
    
    calculator = Tool(
        name="add_numbers",
        description="Add two numbers together",
        function=add_numbers,
        parameters=[
            {
                "name": "a",
                "type": float,
                "description": "First number"
            },
            {
                "name": "b",
                "type": float,
                "description": "Second number"
            }
        ]
    )
    
    # String manipulation tool
    def get_length(text):
        return len(text)
    
    length_tool = Tool(
        name="get_length",
        description="Get the length of a string",
        function=get_length,
        parameters=[
            {
                "name": "text",
                "type": str,
                "description": "The string to measure"
            }
        ]
    )
    
    return [calculator, length_tool]


@pytest.fixture
def sample_tools():
    """Create a set of sample tools for testing."""
    # 1. Simple calculator tool
    def add_numbers(a, b):
        return a + b
    
    calculator = Tool(
        name="add_numbers",
        description="Add two numbers together",
        function=add_numbers,
        parameters=[
            {
                "name": "a",
                "type": float,
                "description": "First number"
            },
            {
                "name": "b",
                "type": float,
                "description": "Second number"
            }
        ]
    )
    
    # 2. String manipulation tool
    def count_words(text):
        return len(text.split())
    
    word_counter = Tool(
        name="count_words",
        description="Count the number of words in a text",
        function=count_words,
        parameters=[
            {
                "name": "text",
                "type": str,
                "description": "The text to count words in"
            }
        ]
    )
    
    # 3. Tool that may raise an error
    def divide_numbers(a, b):
        if b == 0:
            raise ZeroDivisionError("Cannot divide by zero")
        return a / b
    
    divider = Tool(
        name="divide_numbers",
        description="Divide first number by second number",
        function=divide_numbers,
        parameters=[
            {
                "name": "a",
                "type": float,
                "description": "Numerator"
            },
            {
                "name": "b",
                "type": float,
                "description": "Denominator (cannot be zero)"
            }
        ]
    )
    
    return [calculator, word_counter, divider] 