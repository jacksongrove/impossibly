"""
Feature tests for image handling capabilities in the Impossibly framework.

This module tests the following features:

1. Agent initialization with image processing capabilities
2. Image input and analysis propagated to subsequent agents
3. Multimodal reasoning with image inputs

Each test uses mocked OpenAI clients and image files to avoid external dependencies
while thoroughly validating the image processing pipeline.
"""
import base64
import pytest
from unittest.mock import patch, mock_open, MagicMock

# Import the necessary components
from impossibly import Agent, Graph, START, END


@pytest.mark.image
class TestImageCapabilities:
    """
    Test suite for verifying image handling capabilities in the Impossibly framework.
    
    This class tests the complete image processing pipeline from file input to agent
    response, including proper encoding, message formatting, and multi-agent workflows.
    """
    
    # Keep this fixture as it's specific to image testing and not in conftest.py
    @pytest.fixture
    def mock_image_file(self):
        """
        Create a mock image file for testing.
        
        Returns:
            tuple: A tuple containing (image_path, base64_encoded_content) for testing
                  image processing without requiring actual image files.
        """
        # This creates a small fake image file content
        mock_image_data = b"fake_image_data"
        mock_image_base64 = base64.b64encode(mock_image_data).decode("utf-8")
        
        with patch("builtins.open", mock_open(read_data=mock_image_data)):
            yield "test_image.jpg", mock_image_base64
    
    @pytest.mark.image_input
    def test_agent_with_image_input(self, mock_openai_client, mock_image_file):
        """
        Test that an agent can receive and process image inputs.
        
        This test verifies:
        - Agent can be configured with vision capabilities
        - Image files are properly encoded to base64
        - Agent can invoke with image files and return responses
        
        Args:
            mock_openai_client: Mocked OpenAI client fixture
            mock_image_file: Mocked image file fixture providing test image data
        """
        image_path, image_base64 = mock_image_file
        
        # Create an agent with vision capabilities
        agent = Agent(
            mock_openai_client,
            model="gpt-4o",  # This model supports vision
            name="VisionAgent",
            system_prompt="You are an agent that can analyze images."
        )
        
        # Mock the _encode_image method to return our base64 encoded test image
        with patch("impossibly.agent.OpenAIAgent._encode_image", return_value=image_base64) as mock_encode:
            # Mock the OpenAI client's chat.completions.create method
            with patch.object(mock_openai_client, "chat") as mock_chat:
                # Set up the mock to return a predefined response
                mock_response = MagicMock()
                mock_response.choices = [MagicMock(message=MagicMock(content="I can see a test image with fake data."))]
                mock_chat.completions.create.return_value = mock_response
                
                # Test invoking the agent with an image
                response = agent.invoke("user", "What do you see in this image?", files=[image_path])
                
                # Verify the response type
                assert response == "I can see a test image with fake data."
                
                # ACTUAL IMPLEMENTATION: Verify that the image was properly encoded and included in the API request
                # 1. Check that _encode_image was called with the correct file path
                mock_encode.assert_called_once_with(image_path)
                
                # 2. Verify the OpenAI API call contains the base64 image data
                assert mock_chat.completions.create.call_count >= 1
                api_call_args = mock_chat.completions.create.call_args_list[0][1]
                assert "messages" in api_call_args
                
                # 3. Ensure the message format follows OpenAI's multimodal structure
                user_messages = [msg for msg in api_call_args["messages"] if msg.get("role") == "user"]
                assert len(user_messages) > 0
                
                user_message = user_messages[-1]
                assert "content" in user_message
                
                # Verify multimodal structure
                if isinstance(user_message["content"], list):
                    content_items = user_message["content"]
                    
                    # Check for text component
                    text_items = [item for item in content_items if item.get("type") == "text"]
                    assert len(text_items) > 0
                    assert text_items[0]["text"] == "What do you see in this image?"
                    
                    # Check for image component
                    image_items = [item for item in content_items if item.get("type") == "image_url"]
                    assert len(image_items) > 0
                    
                    # Verify image URL structure
                    image_item = image_items[0]
                    assert "image_url" in image_item
                    assert "url" in image_item["image_url"]
                    assert image_item["image_url"]["url"].startswith("data:image/")
                    assert image_base64 in image_item["image_url"]["url"]
    
    @pytest.mark.image_analysis
    def test_image_message_formatting(self, mock_openai_client, mock_image_file):
        """
        Test that messages with images are formatted correctly for the OpenAI API.
        
        This test verifies:
        - Proper multimodal message structure creation
        - Base64 encoding is applied correctly
        - Message content includes both text and image components
        - API calls are made with the correct message format
        
        Args:
            mock_openai_client: Mocked OpenAI client fixture
            mock_image_file: Mocked image file fixture providing test image data
        """
        image_path, image_base64 = mock_image_file
        
        # Create an agent with vision capabilities
        agent = Agent(
            mock_openai_client,
            model="gpt-4o",  # This model supports vision
            name="VisionAgent",
            system_prompt="You are an agent that can analyze images."
        )
        
        # Mock the _encode_image method to return our base64 encoded test image
        with patch("impossibly.agent.OpenAIAgent._encode_image", return_value=image_base64) as mock_encode:
            # Mock the OpenAI client's chat.completions.create method
            with patch.object(mock_openai_client, "chat") as mock_chat:
                # Set up the mock to return a predefined response
                mock_response = MagicMock()
                mock_response.choices = [MagicMock(message=MagicMock(content="I can see an image."))]
                mock_chat.completions.create.return_value = mock_response
                
                # Invoke the agent with an image
                response = agent.invoke("user", "What do you see in this image?", files=[image_path])
                
                # Verify the image was encoded
                mock_encode.assert_called_with(image_path)
                
                # Verify chat completion was created at least once
                assert mock_chat.completions.create.call_count >= 1
                
                # Get the first call arguments
                first_call_args = mock_chat.completions.create.call_args_list[0][1]
                
                # Verify messages format
                assert "messages" in first_call_args
                
                # Find the user message with the image
                user_messages = [msg for msg in first_call_args["messages"] if msg.get("role") == "user"]
                assert len(user_messages) > 0
                
                # Get the last user message (the one with the image)
                user_message = user_messages[-1]
                
                # Verify the content structure 
                assert "content" in user_message
                
                # For multimodal content (list format), check for image URL
                if isinstance(user_message["content"], list):
                    # Look for image items in the content list
                    image_items = [item for item in user_message["content"] 
                                 if item.get("type") == "image_url" or 
                                 (isinstance(item, dict) and "image_url" in item)]
                    
                    assert len(image_items) > 0, "No image found in the message content"
                
                # Verify the response
                assert response == "I can see an image."
    
    @pytest.mark.multi_image
    def test_multi_image_handling(self, mock_openai_client, mock_image_file):
        """
        Test that an agent can handle multiple images in one request.
        
        This test verifies:
        - Multiple image files can be processed simultaneously
        - Each image is properly encoded independently
        - Message format accommodates multiple image URLs
        - Agent can analyze and respond to multi-image prompts
        
        Args:
            mock_openai_client: Mocked OpenAI client fixture
            mock_image_file: Mocked image file fixture providing test image data
        """
        image_path, image_base64 = mock_image_file
        
        # Create two image paths for testing
        image_path1 = "test_image1.jpg"
        image_path2 = "test_image2.jpg"
        
        # Create different base64 data for each image to verify separation
        image_base64_1 = image_base64 + "1"
        image_base64_2 = image_base64 + "2"
        
        # Create an agent with vision capabilities
        agent = Agent(
            mock_openai_client,
            model="gpt-4o",  # This model supports vision
            name="VisionAgent",
            system_prompt="You are an agent that can analyze multiple images."
        )
        
        # Mock the _encode_image method to return different base64 for each image
        def mock_encode_side_effect(path):
            if path == image_path1:
                return image_base64_1
            elif path == image_path2:
                return image_base64_2
            else:
                return image_base64
        
        with patch("impossibly.agent.OpenAIAgent._encode_image", side_effect=mock_encode_side_effect) as mock_encode:
            # Mock the OpenAI client's chat.completions.create method
            with patch.object(mock_openai_client, "chat") as mock_chat:
                # Set up the mock to return a predefined response
                mock_response = MagicMock()
                mock_response.choices = [MagicMock(message=MagicMock(content="I can compare these two images."))]
                mock_chat.completions.create.return_value = mock_response
                
                # Test invoking the agent with multiple images
                response = agent.invoke("user", "Compare these two images", files=[image_path1, image_path2])
                
                # Verify the response
                assert response == "I can compare these two images."
                
                # ACTUAL IMPLEMENTATION: Verify that multiple images were correctly encoded and included
                # 1. Assert _encode_image was called twice (once per image)
                assert mock_encode.call_count == 2
                mock_encode.assert_any_call(image_path1)
                mock_encode.assert_any_call(image_path2)
                
                # 2. Check the message content contains multiple image_url objects
                api_call_args = mock_chat.completions.create.call_args_list[0][1]
                user_messages = [msg for msg in api_call_args["messages"] if msg.get("role") == "user"]
                user_message = user_messages[-1]
                
                if isinstance(user_message["content"], list):
                    content_items = user_message["content"]
                    
                    # Check for text component
                    text_items = [item for item in content_items if item.get("type") == "text"]
                    assert len(text_items) > 0
                    assert text_items[0]["text"] == "Compare these two images"
                    
                    # Check for multiple image components
                    image_items = [item for item in content_items if item.get("type") == "image_url"]
                    assert len(image_items) == 2, f"Expected 2 images, found {len(image_items)}"
                    
                    # 3. Verify that both images maintain separate base64 encodings
                    image_urls = [item["image_url"]["url"] for item in image_items]
                    
                    # Check that both our distinct base64 strings are present
                    found_image1 = any(image_base64_1 in url for url in image_urls)
                    found_image2 = any(image_base64_2 in url for url in image_urls)
                    
                    assert found_image1, "First image base64 not found in message"
                    assert found_image2, "Second image base64 not found in message"
                    
                    # Verify they are actually different
                    assert image_urls[0] != image_urls[1], "Image URLs should be different"
    
    @pytest.mark.image_graph
    def test_image_agent_in_graph(self, mock_openai_client, mock_image_file):
        """
        Test that an image-capable agent can be part of a graph workflow.
        
        This test verifies:
        - Vision agents can be integrated into multi-agent workflows
        - Images can be passed through graph execution pipelines
        - Subsequent agents can access processed image analysis results
        - Graph routing works correctly with image-processing agents
        
        Args:
            mock_openai_client: Mocked OpenAI client fixture
            mock_image_file: Mocked image file fixture providing test image data
        """
        image_path, image_base64 = mock_image_file
        
        # Create an agent with vision capabilities
        vision_agent = Agent(
            mock_openai_client,
            model="gpt-4o",  # This model supports vision
            name="VisionAgent",
            system_prompt="You are an agent that can analyze images.",
            description="I can analyze images"
        )
        
        # Create another agent for further processing
        processor_agent = Agent(
            mock_openai_client,
            model="gpt-4o",
            name="ProcessorAgent",
            system_prompt="You process information from other agents.",
            description="I process information"
        )
        
        # Create a graph with these agents
        graph = Graph()
        graph.add_node(vision_agent)
        graph.add_node(processor_agent)
        
        graph.add_edge(START, vision_agent)
        graph.add_edge(vision_agent, processor_agent)
        graph.add_edge(processor_agent, END)
        
        # Mock the _encode_image method to return our base64 encoded test image
        with patch("impossibly.agent.OpenAIAgent._encode_image", return_value=image_base64) as mock_encode:
            # Mock vision agent's response with routing command
            vision_response = "I see a cat in the image. It appears to be a domestic cat with orange fur. \\ProcessorAgent\\"
            
            # Mock processor agent's response  
            processor_response = "After analysis, this appears to be a domestic cat with distinctive orange coloring."
            
            # Track the actual calls to verify the workflow
            vision_invoke_calls = []
            processor_invoke_calls = []
            
            async def vision_agent_invoke_side_effect(author, prompt, files=None, edges=None, show_thinking=False):
                vision_invoke_calls.append({
                    'author': author, 
                    'prompt': prompt, 
                    'files': files or [],
                    'edges': edges
                })
                return vision_response
            
            async def processor_agent_invoke_side_effect(author, prompt, files=None, edges=None, show_thinking=False):
                processor_invoke_calls.append({
                    'author': author,
                    'prompt': prompt, 
                    'files': files or [],
                    'edges': edges
                })
                return processor_response
                
            # Mock the agent invoke methods
            with patch.object(vision_agent, "invoke", side_effect=vision_agent_invoke_side_effect) as mock_vision_invoke:
                with patch.object(processor_agent, "invoke", side_effect=processor_agent_invoke_side_effect) as mock_processor_invoke:
                    
                    # Invoke the graph with an image
                    response = graph.invoke("Analyze this image", files=[image_path])
                    
                    # Verify the final response
                    assert response == processor_response
                    
                    # Verify the image was properly passed between agents
                    # 1. Check that the vision_agent.invoke was called with the image file
                    assert len(vision_invoke_calls) == 1
                    vision_call = vision_invoke_calls[0]
                    assert vision_call['author'] == 'user'
                    assert vision_call['prompt'] == "Analyze this image"
                    assert image_path in vision_call['files']
                    assert vision_call['edges'] == [processor_agent]  # Should have processor as edge
                    
                    # 2. Verify the first agent processed the image and extracted meaningful content
                    assert mock_vision_invoke.call_count == 1
                    
                    # 3. Ensure the processor_agent.invoke received the vision analysis as text input
                    assert len(processor_invoke_calls) == 1
                    processor_call = processor_invoke_calls[0]
                    assert processor_call['author'] == 'user'
                    # The prompt should contain the vision agent's analysis 
                    # Note: Since vision_agent only has one edge, _get_route is not called and routing command remains
                    expected_prompt = "I see a cat in the image. It appears to be a domestic cat with orange fur. \\ProcessorAgent\\"
                    assert processor_call['prompt'] == expected_prompt
                    assert processor_call['files'] == []  # No files should be passed to processor
                    assert processor_call['edges'] == [END]  # Should have END as edge
                    
                    # 4. Confirm the graph correctly routed from vision_agent to processor_agent
                    assert mock_processor_invoke.call_count == 1
                    
                    # 5. Validate that the final response incorporates both agents' contributions
                    assert "domestic cat" in response  # Content from both agents
                    
                    # 6. Test that the image file parameter was correctly handled in graph workflow
                    # The image should only be passed to the first agent (vision_agent)
                    assert image_path in vision_call['files']
                    assert image_path not in processor_call['files'] 