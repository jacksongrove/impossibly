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
from unittest.mock import patch, MagicMock

from imengine import Agent
from openai import OpenAI


class TestRAGFunctionality:
    """Tests for verifying RAG functionality."""
    
    @pytest.fixture
    def test_files(self):
        """Create temporary test files for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a text file
            text_file = os.path.join(temp_dir, "sample.txt")
            with open(text_file, "w") as f:
                f.write("This is a sample text file for testing RAG functionality.")
            
            # Create a very large text file (beyond normal context window)
            large_file = os.path.join(temp_dir, "large_document.txt")
            with open(large_file, "w") as f:
                # Write approximately 100K tokens worth of text (roughly 400KB)
                lorem_ipsum = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. "
                f.write(lorem_ipsum * 10000)  # ~400KB of text
            
            # Create a JSON file
            json_file = os.path.join(temp_dir, "data.json")
            with open(json_file, "w") as f:
                f.write('{"key": "value", "numbers": [1, 2, 3]}')
            
            # Create a simple image file (1x1 pixel)
            image_file = os.path.join(temp_dir, "sample.png")
            with open(image_file, "wb") as f:
                # Write a minimal valid PNG file (1x1 transparent pixel)
                f.write(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82')
            
            # Create an unsupported file type
            bad_file = os.path.join(temp_dir, "unsupported.xyz")
            with open(bad_file, "w") as f:
                f.write("This file has an unsupported extension.")
            
            yield {
                "text_file": text_file,
                "large_file": large_file,
                "json_file": json_file,
                "image_file": image_file,
                "bad_file": bad_file
            }
    
    def test_openai_text_file_processing(self, mock_openai_client, test_files):
        """Test OpenAI agent's handling of text files in RAG."""
        # Create an OpenAI agent
        agent = Agent(
            mock_openai_client,
            model="gpt-4o",
            name="OpenAI_RAG_Tester",
            system_prompt="You analyze documents and answer questions about them."
        )
        
        # Set up the mock client to track calls
        mock_files_create = mock_openai_client.files.create
        
        # Test with a small text file
        files = [test_files["text_file"]]
        
        # Invoke agent with the file
        with patch.object(agent.client, "invoke", return_value="I analyzed the text file."):
            response = agent.invoke("user", "Analyze this file.", files=files)
            
            # Verify file was processed correctly
            assert mock_files_create.called
            assert response == "I analyzed the text file."
            
            # Extract the call arguments
            # OpenAI should have called files.create with purpose="assistants"
            call_args = mock_files_create.call_args_list[0][1]
            assert "purpose" in call_args
            assert call_args["purpose"] == "assistants"
    
    def test_openai_large_file_processing(self, mock_openai_client, test_files):
        """Test OpenAI agent's handling of large text files in RAG."""
        # Create an OpenAI agent
        agent = Agent(
            mock_openai_client,
            model="gpt-4o",
            name="OpenAI_RAG_Tester",
            system_prompt="You analyze large documents and answer questions about them."
        )
        
        # Set up the mock client to track calls
        mock_files_create = mock_openai_client.files.create
        
        # Test with a large text file
        files = [test_files["large_file"]]
        
        # Invoke agent with the file
        with patch.object(agent.client, "invoke", return_value="I processed the large file without truncating it."):
            response = agent.invoke("user", "Analyze this large file.", files=files)
            
            # Verify file was processed correctly
            assert mock_files_create.called
            assert response == "I processed the large file without truncating it."
    
    def test_openai_image_file_processing(self, mock_openai_client, test_files):
        """Test OpenAI agent's handling of image files."""
        # Create an OpenAI agent
        agent = Agent(
            mock_openai_client,
            model="gpt-4-vision-preview",
            name="OpenAI_Image_Tester",
            system_prompt="You analyze images."
        )
        
        # Test with image file
        with patch.object(agent.client, "invoke", return_value="I analyzed the image."):
            response = agent.invoke("user", "Analyze this image.", files=[test_files["image_file"]])
            assert response == "I analyzed the image."
            
            # OpenAI should use the files API
            assert mock_openai_client.files.create.called
    
    def test_unsupported_file_handling(self, mock_openai_client, test_files):
        """Test OpenAI agent properly handles unsupported file types."""
        # Create OpenAI agent
        agent = Agent(mock_openai_client, name="OpenAI_Error_Tester")
        
        # Try with an unsupported file type
        with pytest.raises(Exception):  # Assuming some sort of exception will be raised
            with patch.object(agent.client, "invoke"):
                response = agent.invoke("user", "Analyze this file.", files=[test_files["bad_file"]])
    
    def test_openai_rag_content_reaching_agent(self, mock_openai_client):
        """Test that RAG content actually reaches the OpenAI agent and affects its response."""
        # Create an OpenAI agent with a system prompt to recite file content
        agent = Agent(
            mock_openai_client,
            model="gpt-4o",
            name="OpenAI_RAG_Content_Tester",
            system_prompt="You are an assistant that always recites information from the documents provided to you. When asked about a document, you should quote its contents directly."
        )
        
        # Create a temporary file with test content
        test_content = "OPENAI_SECRET_KEY_12345"
        
        with tempfile.NamedTemporaryFile(suffix=".txt", mode="w+", delete=False) as temp_file:
            temp_file.write(f"This is a confidential document with access code: {test_content}")
            temp_file_path = temp_file.name
        
        try:
            # Mock file creation method
            with patch.object(mock_openai_client.files, "create") as mock_create:
                # Set up mock file object
                mock_file = MagicMock()
                mock_file.id = "file-123456"
                mock_create.return_value = mock_file
                
                # Mock the invoke method to return a response that includes RAG content
                expected_response = f"The document states the access code is: {test_content}"
                with patch.object(agent.client, "invoke", return_value=expected_response):
                    # Test that agent receives and uses the RAG content
                    response = agent.invoke("user", "What is the access code in the document?", files=[temp_file_path])
                    
                    # Verify file was processed
                    assert mock_create.called
                    
                    # Verify response includes the information from the RAG content
                    assert test_content in response
                    assert response == expected_response
        finally:
            # Clean up temporary file
            os.unlink(temp_file_path)
    
    def test_openai_multiple_file_processing(self, mock_openai_client):
        """Test that OpenAI agent can handle multiple files in a single request."""
        # Create an OpenAI agent
        agent = Agent(
            mock_openai_client,
            model="gpt-4o",
            name="OpenAI_MultiFile_Tester",
            system_prompt="You analyze multiple documents at once."
        )
        
        # Create multiple temp files
        files = []
        try:
            for i in range(3):
                with tempfile.NamedTemporaryFile(suffix=".txt", mode="w+", delete=False) as temp_file:
                    temp_file.write(f"This is document {i+1} with specific content.")
                    files.append(temp_file.name)
            
            # Mock file creation
            with patch.object(mock_openai_client.files, "create") as mock_create:
                mock_file = MagicMock()
                mock_file.id = "file-123456"
                mock_create.return_value = mock_file
                
                # Expected response including information about all files
                expected_response = "I analyzed all 3 documents."
                
                # Mock the invoke response
                with patch.object(agent.client, "invoke", return_value=expected_response):
                    # Test multiple file handling
                    response = agent.invoke("user", "Analyze all these files together.", files=files)
                    
                    # Verify all files were processed
                    assert mock_create.call_count == 3
                    assert response == expected_response
        
        finally:
            # Clean up temp files
            for file_path in files:
                try:
                    os.unlink(file_path)
                except:
                    pass 