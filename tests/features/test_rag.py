"""
Feature tests for Retrieval-Augmented Generation (RAG) capabilities for OpenAI (Anthropic not supported).

This tests the following features:
1. Text file processing by OpenAI agents
2. Image file processing by OpenAI agents
3. Handling of large text files without truncation
4. Proper error handling for unsupported file types
"""
import os
import pytest
import tempfile
import json
from unittest.mock import patch, MagicMock, call
from impossibly import Agent
from tests.utils.client_mocks import MockOpenAI


@pytest.mark.rag
class TestRAGFunctionality:
    """Tests for verifying RAG functionality."""
    
    @pytest.fixture
    def test_files(self):
        """Create temporary test files for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a text file with unique identifiable content
            text_file = os.path.join(temp_dir, "document.txt")
            text_content = "This is a test document with UNIQUE_IDENTIFIER_TEXT_12345."
            with open(text_file, "w") as f:
                f.write(text_content)
            
            # Create a large text file with unique identifiable content
            large_file = os.path.join(temp_dir, "large_document.txt")
            large_content = "This is a large document with UNIQUE_IDENTIFIER_LARGE_67890.\n" * 100
            with open(large_file, "w") as f:
                f.write(large_content)
            
            # Create a JSON file with unique identifiable content
            json_file = os.path.join(temp_dir, "data.json")
            json_content = {"key": "value", "unique_id": "UNIQUE_IDENTIFIER_JSON_ABCDE"}
            with open(json_file, "w") as f:
                f.write(json.dumps(json_content))
            
            # Create an image file with metadata for testing
            image_file = os.path.join(temp_dir, "sample.png")
            with open(image_file, "w") as f:
                f.write("UNIQUE_IDENTIFIER_IMAGE_FGHIJ")
            
            # Create an unsupported file type
            bad_file = os.path.join(temp_dir, "unsupported.xyz")
            with open(bad_file, "w") as f:
                f.write("This file has an unsupported extension")
            
            yield {
                "text_file": text_file,
                "text_content": text_content,
                "large_file": large_file,
                "large_content": large_content,
                "json_file": json_file,
                "json_content": json_content,
                "image_file": image_file,
                "image_content": "UNIQUE_IDENTIFIER_IMAGE_FGHIJ",
                "bad_file": bad_file,
            }
    
    @pytest.mark.rag_text
    def test_openai_text_file_processing(self, mock_openai_client, test_files):
        """Test OpenAI agent's handling of text files in RAG."""
        # Track file_ids passed to completions.create
        file_ids = []
        # Track if file upload was triggered
        file_uploaded = False
        
        # Mock the files.create method to verify it's called
        original_create = mock_openai_client.files.create
        def mock_files_create(*args, **kwargs):
            nonlocal file_uploaded
            file_uploaded = True
            return original_create(*args, **kwargs)
        mock_openai_client.files.create = mock_files_create
        
        # Custom mock implementation that captures file_ids
        def mock_completions_create(*args, **kwargs):
            # Extract and store file_ids if they exist in the request
            if 'file_ids' in kwargs:
                file_ids.extend(kwargs['file_ids'])
            
            # Create response incorporating the unique identifier from the text file
            mock_content = f"I found {test_files['text_content']} in the document"
            mock_message = MagicMock()
            mock_message.content = mock_content
            mock_choice = MagicMock()
            mock_choice.message = mock_message
            mock_response = MagicMock()
            mock_response.choices = [mock_choice]
            return mock_response
        
        # Replace the default mock with our custom implementation
        mock_openai_client.chat.completions.create.side_effect = mock_completions_create
        
        # Create agent with text file
        agent = Agent(mock_openai_client, files=[test_files["text_file"]])
        
        # Verify file was initialized
        assert len(agent.files) == 1, "Text file should be initialized for RAG"
        assert agent.files[0].id == "mock-file-id", "File ID should be initialized"
        assert file_uploaded, "File upload should have been triggered"
        
        # Test invoking the agent with a prompt
        response = agent.invoke("user", "Tell me about the document")
        
        # Verify the response contains the unique identifier from the text file
        assert "UNIQUE_IDENTIFIER_TEXT_12345" in response, "Response should contain content from the file"
        
        # Verify that at least one API call was made
        assert mock_openai_client.chat.completions.create.call_count > 0, "API should be called"
    
    @pytest.mark.rag_large
    def test_openai_large_file_processing(self, mock_openai_client, test_files):
        """Test OpenAI agent's handling of large text files in RAG."""
        # Track file_ids passed to completions.create
        file_ids = []
        # Track if file upload was triggered
        file_uploaded = False
        
        # Mock the files.create method to verify it's called
        original_create = mock_openai_client.files.create
        def mock_files_create(*args, **kwargs):
            nonlocal file_uploaded
            file_uploaded = True
            return original_create(*args, **kwargs)
        mock_openai_client.files.create = mock_files_create
        
        # Custom mock implementation that captures file_ids
        def mock_completions_create(*args, **kwargs):
            # Extract and store file_ids if they exist in the request
            if 'file_ids' in kwargs:
                file_ids.extend(kwargs['file_ids'])
            
            # Create response incorporating the unique identifier from the large file
            mock_content = f"I found {test_files['large_content'][:100]} in the document"
            mock_message = MagicMock()
            mock_message.content = mock_content
            mock_choice = MagicMock()
            mock_choice.message = mock_message
            mock_response = MagicMock()
            mock_response.choices = [mock_choice]
            return mock_response
        
        # Replace the default mock with our custom implementation
        mock_openai_client.chat.completions.create.side_effect = mock_completions_create
        
        # Create agent with large text file
        agent = Agent(mock_openai_client, files=[test_files["large_file"]])
        
        # Verify file was initialized
        assert len(agent.files) == 1, "Large file should be initialized for RAG"
        assert file_uploaded, "File upload should have been triggered"
        
        # Test invoking the agent with a prompt
        response = agent.invoke("user", "Summarize the large document")
        
        # Verify the response contains the unique identifier from the large file
        assert "UNIQUE_IDENTIFIER_LARGE_67890" in response, "Response should contain content from the file"
        
        # Verify that at least one API call was made
        assert mock_openai_client.chat.completions.create.call_count > 0, "API should be called"
    
    @pytest.mark.rag_image
    def test_openai_image_file_processing(self, mock_openai_client, test_files):
        """Test OpenAI agent's handling of image files."""
        # Track file_ids passed to completions.create
        file_ids = []
        # Track if file upload was triggered
        file_uploaded = False
        
        # Mock the files.create method to verify it's called
        original_create = mock_openai_client.files.create
        def mock_files_create(*args, **kwargs):
            nonlocal file_uploaded
            file_uploaded = True
            return original_create(*args, **kwargs)
        mock_openai_client.files.create = mock_files_create
        
        # Custom mock implementation that captures file_ids
        def mock_completions_create(*args, **kwargs):
            # Extract and store file_ids if they exist in the request
            if 'file_ids' in kwargs:
                file_ids.extend(kwargs['file_ids'])
            
            # Create response referencing the image content
            mock_content = f"The image contains {test_files['image_content']}"
            mock_message = MagicMock()
            mock_message.content = mock_content
            mock_choice = MagicMock()
            mock_choice.message = mock_message
            mock_response = MagicMock()
            mock_response.choices = [mock_choice]
            return mock_response
        
        # Replace the default mock with our custom implementation
        mock_openai_client.chat.completions.create.side_effect = mock_completions_create
        
        # Create agent with image file
        agent = Agent(mock_openai_client, files=[test_files["image_file"]])
        
        # Verify file was initialized
        assert len(agent.files) == 1, "Image file should be initialized for RAG"
        assert file_uploaded, "File upload should have been triggered"
        
        # Test invoking the agent with a prompt
        response = agent.invoke("user", "Describe the image")
        
        # Verify the response contains the unique identifier from the image file
        assert "UNIQUE_IDENTIFIER_IMAGE_FGHIJ" in response, "Response should contain content from the file"
        
        # Verify that at least one API call was made
        assert mock_openai_client.chat.completions.create.call_count > 0, "API should be called"
    
    @pytest.mark.rag_unsupported
    def test_unsupported_file_handling(self, mock_openai_client, test_files):
        """Test OpenAI agent properly handles unsupported file types."""
        # Create agent with unsupported file
        with patch('builtins.print') as mock_print:
            agent = Agent(mock_openai_client, files=[test_files["bad_file"]])
            
            # Verify file was not initialized (since it's unsupported)
            assert len(agent.files) == 0, "Unsupported file should not be initialized for RAG"
            
            # Verify warning message was printed
            mock_print.assert_called_once()
            # Get the first positional argument of the first call
            call_args = mock_print.call_args[0][0]
            # Check that the string contains our expected text
            assert "Unsupported file type" in str(call_args), f"Expected warning about unsupported file type, got: {call_args}"
    
    @pytest.mark.rag_content
    def test_openai_rag_content_reaching_agent(self, mock_openai_client):
        """Test that RAG content actually reaches the OpenAI agent and affects its response."""
        # Create a temporary file with specific content to test
        with tempfile.NamedTemporaryFile(suffix=".txt", mode="w") as temp_file:
            # Write content to the file with a unique identifier
            unique_content = "Unique identifier: XYZ-123-ABC"
            temp_file.write(unique_content)
            temp_file.flush()
            
            # Track all params passed to completions.create
            create_params = []
            # Track if file upload was triggered
            file_uploaded = False
            
            # Mock the files.create method to verify it's called
            original_create = mock_openai_client.files.create
            def mock_files_create(*args, **kwargs):
                nonlocal file_uploaded
                file_uploaded = True
                return original_create(*args, **kwargs)
            mock_openai_client.files.create = mock_files_create
            
            # Custom mock implementation that tracks all parameters
            def mock_completions_create(*args, **kwargs):
                # Store all params for later verification
                create_params.append(kwargs)
                
                # Create response referencing the file content
                mock_content = f"Response referencing {unique_content}"
                mock_message = MagicMock()
                mock_message.content = mock_content
                mock_choice = MagicMock()
                mock_choice.message = mock_message
                mock_response = MagicMock()
                mock_response.choices = [mock_choice]
                return mock_response
            
            # Replace the default mock with our custom implementation
            mock_openai_client.chat.completions.create.side_effect = mock_completions_create
            
            # Create agent with the file
            agent = Agent(mock_openai_client, files=[temp_file.name])
            
            # Verify file was uploaded
            assert file_uploaded, "File upload should have been triggered"
            
            # Test invoking the agent with a prompt specifically asking about the content
            response = agent.invoke("user", f"Find and tell me about {unique_content}")
            
            # Verify file details were passed in the API call
            assert len(create_params) > 0, "API should be called with parameters"
            
            # Verify the response contains the unique identifier
            assert unique_content in response, "Agent response should include the unique content from the file"
            
            # Verify the OpenAI client was called
            assert mock_openai_client.chat.completions.create.call_count > 0, "OpenAI client should be called"
    
    @pytest.mark.rag_multiple
    def test_openai_multiple_file_processing(self, mock_openai_client):
        """Test that OpenAI agent can handle multiple files in a single request."""
        # Create temporary files with unique identifiers
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create first file with unique identifier
            file1_path = os.path.join(temp_dir, "file1.txt")
            file1_content = "Content of file 1 with ID: MULTI_FILE_ID_1"
            with open(file1_path, "w") as f:
                f.write(file1_content)
            
            # Create second file with unique identifier
            file2_path = os.path.join(temp_dir, "file2.json")
            file2_content = {"key": "Content of file 2 with ID: MULTI_FILE_ID_2"}
            with open(file2_path, "w") as f:
                f.write(json.dumps(file2_content))
            
            # Track each chat.completions.create call's file_ids parameter
            api_calls = []
            
            # Custom mock implementation that captures file_ids and references content
            def mock_completions_create(*args, **kwargs):
                # Store the file_ids from this API call
                if 'file_ids' in kwargs:
                    api_calls.append(kwargs['file_ids'])
                
                # Create response incorporating unique IDs from both files
                mock_content = f"Found content: MULTI_FILE_ID_1 and MULTI_FILE_ID_2 in the files"
                mock_message = MagicMock()
                mock_message.content = mock_content
                mock_choice = MagicMock()
                mock_choice.message = mock_message
                mock_response = MagicMock()
                mock_response.choices = [mock_choice]
                return mock_response
            
            # Replace the default mock
            mock_openai_client.chat.completions.create.side_effect = mock_completions_create
            
            # Create agent with multiple files - use a special mock for each file
            with patch.object(mock_openai_client.files, 'create') as mock_create:
                # Create different mock file objects for each file
                mock_file1 = MagicMock(id="mock-file-id-1")
                mock_file2 = MagicMock(id="mock-file-id-2")
                
                # Return different mock files for each call
                mock_create.side_effect = [mock_file1, mock_file2]
                
                # Create the agent with both files
                agent = Agent(mock_openai_client, files=[file1_path, file2_path])
                
                # Verify both files were initialized with different IDs
                assert len(agent.files) == 2, "Both files should be initialized for RAG"
                assert agent.files[0].id == "mock-file-id-1"
                assert agent.files[1].id == "mock-file-id-2"
                
                # Verify files.create was called twice with different file paths
                assert mock_create.call_count == 2
                assert mock_create.call_args_list[0].kwargs['file'].name == file1_path
                assert mock_create.call_args_list[1].kwargs['file'].name == file2_path
            
                # Test invoking the agent with a prompt asking about both files
                response = agent.invoke("user", "Compare the content of both files")
                
                # Verify that OpenAI API was called
                assert mock_openai_client.chat.completions.create.call_count > 0, "OpenAI API should be called"
                
                # Verify the response contains both unique identifiers
                assert "MULTI_FILE_ID_1" in response, "Response should contain content from file 1"
                assert "MULTI_FILE_ID_2" in response, "Response should contain content from file 2" 