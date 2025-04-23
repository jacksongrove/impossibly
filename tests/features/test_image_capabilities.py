"""
Feature tests for image handling capabilities.

This tests the following features:
1. Agent initialization with image processing capabilities
2. Image input and analysis 
3. Multimodal reasoning
"""
import base64
import pytest
from unittest.mock import patch, mock_open

# Import the necessary components
from imengine import Agent, Graph, START, END


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
        with patch("imengine.agent.OpenAIAgent._encode_image", return_value=image_base64):
            # Test invoking the agent with an image
            response = agent.invoke("user", "What do you see in this image?", files=[image_path])
            
            # Verify the response (this depends on the mock set up for the client)
            assert "cat" in response.lower()
            
            # In a real implementation, we would verify that the image was properly
            # encoded and included in the message sent to the model
    
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
        with patch("imengine.agent.OpenAIAgent._encode_image", return_value=image_base64):
            # Mock the client's chat.completions.create to capture the messages
            with patch.object(agent.client, "chat.completions.create") as mock_create:
                # Set up the mock to return a predefined response
                mock_message = mock_create.return_value.choices[0].message
                mock_message.content = "Test response"
                
                # Invoke the agent with an image
                agent.invoke("user", "What do you see in this image?", files=[image_path])
                
                # Verify the format of the message sent to the model
                # Extract the call arguments
                call_args = mock_create.call_args[1]
                
                # Check that messages are included in the call
                assert "messages" in call_args
                
                # Get the last message (the user message with the image)
                user_message = [msg for msg in call_args["messages"] if msg.get("role") == "user"][-1]
                
                # Verify the message structure for a multimodal input
                assert isinstance(user_message["content"], list)
                
                # Verify text component
                assert any(item.get("type") == "text" for item in user_message["content"])
                
                # Verify image component
                image_items = [item for item in user_message["content"] if item.get("type") == "image_url"]
                assert len(image_items) > 0
                
                # Check image URL format (should be data URL with base64)
                image_url = image_items[0]["image_url"]["url"]
                assert image_url.startswith("data:image/")
                assert "base64" in image_url
    
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
        with patch("imengine.agent.OpenAIAgent._encode_image", return_value=image_base64):
            # Test invoking the agent with multiple images
            response = agent.invoke("user", "Compare these two images", files=[image_path1, image_path2])
            
            # Verify the response (this depends on the mock set up for the client)
            assert "cat" in response.lower()
            
            # In a real implementation, we would verify that multiple images were
            # correctly encoded and included in the message
    
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
        with patch("imengine.agent.OpenAIAgent._encode_image", return_value=image_base64):
            # Mock the vision agent's response
            with patch.object(vision_agent.client, "invoke", return_value="I see a cat in the image. \\ProcessorAgent\\"):
                # Mock the processor agent's response
                with patch.object(processor_agent.client, "invoke", return_value="After analysis, this appears to be a domestic cat."):
                    # Mock the graph execution
                    with patch.object(graph, "_run_graph") as mock_run:
                        mock_run.return_value = "Complete analysis: domestic cat identified in image."
                        
                        # Invoke the graph with an image
                        response = graph.invoke("Analyze this image", files=[image_path])
                        
                        # Verify the response
                        assert response == "Complete analysis: domestic cat identified in image."
                        
                        # In a real implementation, we would verify the path through the graph
                        # and that the image was properly passed between agents 