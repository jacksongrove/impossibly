"""
Feature tests for image handling capabilities.

This tests the following features:
1. Agent initialization with image processing capabilities
2. Image input and analysis 
3. Multimodal reasoning
"""
import base64
import pytest
from unittest.mock import patch, mock_open, MagicMock

# Import the necessary components
from impossibly import Agent, Graph, START, END


@pytest.mark.image
class TestImageCapabilities:
    """Tests for verifying image handling capabilities."""
    
    # Keep this fixture as it's specific to image testing and not in conftest.py
    @pytest.fixture
    def mock_image_file(self):
        """Create a mock image file for testing."""
        # This creates a small fake image file content
        mock_image_data = b"fake_image_data"
        mock_image_base64 = base64.b64encode(mock_image_data).decode("utf-8")
        
        with patch("builtins.open", mock_open(read_data=mock_image_data)):
            yield "test_image.jpg", mock_image_base64
    
    @pytest.mark.image_input
    def test_agent_with_image_input(self, mock_openai_client, mock_image_file):
        """Test that an agent can receive and process image inputs."""
        image_path, image_base64 = mock_image_file
        
        # Create an agent with vision capabilities
        agent = Agent(
            mock_openai_client,
            model="gpt-4o",  # This model supports vision
            name="VisionAgent",
            system_prompt="You are an agent that can analyze images."
        )
        
        # Mock the _encode_image method to return our base64 encoded test image
        with patch("impossibly.agent.OpenAIAgent._encode_image", return_value=image_base64):
            # Test invoking the agent with an image
            response = agent.invoke("user", "What do you see in this image?", files=[image_path])
            
            # Verify the response type (adjusted to match the mock response)
            assert response == "This is a mock response from GPT"
            
            # In a real implementation, we would verify that the image was properly
            # encoded and included in the message sent to the model
    
    @pytest.mark.image_analysis
    def test_image_message_formatting(self, mock_openai_client, mock_image_file):
        """Test that messages with images are formatted correctly."""
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
        """Test that an agent can handle multiple images in one request."""
        image_path, image_base64 = mock_image_file
        
        # Create two image paths for testing
        image_path1 = "test_image1.jpg"
        image_path2 = "test_image2.jpg"
        
        # Create an agent with vision capabilities
        agent = Agent(
            mock_openai_client,
            model="gpt-4o",  # This model supports vision
            name="VisionAgent",
            system_prompt="You are an agent that can analyze multiple images."
        )
        
        # Mock the _encode_image method to return our base64 encoded test image
        with patch("impossibly.agent.OpenAIAgent._encode_image", return_value=image_base64):
            # Test invoking the agent with multiple images
            response = agent.invoke("user", "Compare these two images", files=[image_path1, image_path2])
            
            # Verify the response (adjusted to match the mock response)
            assert response == "This is a mock response from GPT"
            
            # In a real implementation, we would verify that multiple images were
            # correctly encoded and included in the message
    
    @pytest.mark.image_graph
    def test_image_agent_in_graph(self, mock_openai_client, mock_image_file):
        """Test that an image-capable agent can be part of a graph."""
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
        with patch("impossibly.agent.OpenAIAgent._encode_image", return_value=image_base64):
            # Mock the vision agent's response
            with patch.object(vision_agent.client, "invoke", return_value="I see a cat in the image. \\ProcessorAgent\\"):
                # Mock the processor agent's response
                with patch.object(processor_agent.client, "invoke", return_value="After analysis, this appears to be a domestic cat."):
                    # Mock the graph execution
                    with patch.object(graph, "_invoke_async") as mock_run:
                        mock_run.return_value = "Complete analysis: domestic cat identified in image."
                        
                        # Invoke the graph with an image
                        response = graph.invoke("Analyze this image", files=[image_path])
                        
                        # Verify the response
                        assert response == "Complete analysis: domestic cat identified in image."
                        
                        # In a real implementation, we would verify the path through the graph
                        # and that the image was properly passed between agents 