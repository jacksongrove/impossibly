"""
Mock clients for testing.

This module provides functions to create mock clients that will pass isinstance checks
while also providing the necessary structure for testing.
"""
from unittest.mock import MagicMock
from anthropic import Anthropic
from openai import OpenAI


class MockAnthropic(Anthropic):
    """A class that inherits from Anthropic for isinstance checks."""
    
    def __init__(self):
        # Don't call super().__init__() because it requires API keys
        # Instead, just set up the required attributes for testing
        self.messages = MagicMock()
        mock_response = MagicMock()
        mock_content_block = MagicMock()
        mock_content_block.type = "text"
        mock_content_block.text = "This is a mock response from Claude"
        mock_response.content = [mock_content_block]
        self.messages.create.return_value = mock_response


class MockOpenAI(OpenAI):
    """A class that inherits from OpenAI for isinstance checks."""
    
    def __init__(self):
        # Don't call super().__init__() because it requires API keys
        # Instead, just set up the required attributes for testing
        
        # Set up chat.completions.create
        self.chat = MagicMock()
        self.chat.completions = MagicMock()
        mock_message = MagicMock()
        mock_message.content = "This is a mock response from GPT"
        mock_choice = MagicMock()
        mock_choice.message = mock_message
        mock_response = MagicMock()
        mock_response.choices = [mock_choice]
        self.chat.completions.create.return_value = mock_response
        
        # Set up files API with better support for RAG testing
        self.files = MagicMock()
        mock_file = MagicMock()
        mock_file.id = "mock-file-id"
        mock_file.filename = "mock-file.txt"
        mock_file.purpose = "assistants"
        mock_file.bytes = 1024
        self.files.create.return_value = mock_file
        
        # List files returns a list of files
        self.files.list.return_value = MagicMock(data=[mock_file])
        
        # Retrieve file returns a single file
        self.files.retrieve.return_value = mock_file
        
        # Delete file returns a confirmation of deletion
        delete_response = MagicMock()
        delete_response.deleted = True
        self.files.delete.return_value = delete_response


def create_mock_anthropic():
    """Create a mock Anthropic client that will pass isinstance checks."""
    return MockAnthropic()


def create_mock_openai():
    """Create a mock OpenAI client that will pass isinstance checks."""
    return MockOpenAI() 