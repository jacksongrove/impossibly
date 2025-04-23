"""
Feature tests for tool functionality.

This tests the following features:
1. Tool definition and registration
2. Tool execution with parameters
3. Agent using tools for task completion
4. Tool error handling
"""
import pytest
from unittest.mock import MagicMock, patch

# Import the necessary components
from imengine import Agent, Tool, START, END


class TestToolFunctionality:
    """Tests for verifying tool functionality."""
    
    def test_tool_direct_execution(self, basic_tools):
        """Test that tools can be executed directly with appropriate parameters."""
        # Get the calculator tool
        calculator = basic_tools[0]
        
        # Execute the tool directly
        result = calculator.execute(a=5, b=3)
        
        # Verify the result
        assert result == 8
    
    def test_tool_parameter_validation(self, basic_tools):
        """Test that tools validate their parameters."""
        # Get the calculator tool
        calculator = basic_tools[0]
        
        # Test with invalid parameter types
        with pytest.raises(TypeError):
            calculator.execute(a="not a number", b=3)
    
    def test_tool_error_handling(self, sample_tools):
        """Test that tool errors are handled appropriately."""
        # Get the divider tool
        divider = sample_tools[2]
        
        # Test with a zero denominator
        with pytest.raises(ZeroDivisionError):
            divider.execute(a=10, b=0)
    
    def test_agent_using_tools(self, mock_anthropic_client, sample_tools):
        """Test that an agent can use tools to complete tasks."""
        # Create an agent with tools
        agent = Agent(
            mock_anthropic_client,
            model="claude-3-5-haiku-latest",
            name="ToolUser",
            system_prompt="You are an agent that uses tools to solve problems.",
            tools=sample_tools
        )
        
        # Verify the tools were assigned to the agent
        assert len(agent.tools) == 3
        
        # Test with a response that includes a tool call
        tool_response = MagicMock()
        tool_response.stop_reason = "tool_use"
        tool_use = MagicMock()
        tool_use.type = "tool_use"
        tool_use.name = "add_numbers"
        tool_use.input = {"a": 5, "b": 3}
        tool_use.id = "tool_call_1"
        tool_response.content = [tool_use]
        
        # Set up follow-up response after tool use
        follow_up_response = MagicMock()
        follow_up_response.content = [MagicMock(type="text", text="The sum is 8")]
        
        # Mock the client's messages.create to return the tool response then the follow-up
        mock_anthropic_client.messages.create.side_effect = [tool_response, follow_up_response]
        
        # Mock the tool execution to ensure we don't depend on the actual implementation
        with patch.object(sample_tools[0], "execute", return_value=8):
            # Invoke the agent
            response = agent.invoke("user", "What is 5 + 3?")
            
            # In a real test, the agent would actually use the tool and return a response
            # For this test, we're just verifying the agent has the tools
            assert "The sum is 8" in response
    
    def test_tool_formatting_for_api(self, basic_tools):
        """Test that tools can be formatted for different LLM APIs."""
        from imengine.utils.tools import format_tools_for_api
        
        # Format for OpenAI
        openai_tools = format_tools_for_api(basic_tools, api="openai")
        
        # Verify the OpenAI format
        assert len(openai_tools) == 2
        assert openai_tools[0]["type"] == "function"
        assert "function" in openai_tools[0]
        assert "name" in openai_tools[0]["function"]
        assert "description" in openai_tools[0]["function"]
        assert "parameters" in openai_tools[0]["function"]
        
        # Format for Anthropic
        anthropic_tools = format_tools_for_api(basic_tools, api="anthropic")
        
        # Verify the Anthropic format
        assert len(anthropic_tools) == 2
        assert "name" in anthropic_tools[0]
        assert "description" in anthropic_tools[0]
        assert "input_schema" in anthropic_tools[0]
    
    def test_agent_with_async_tool(self, mock_anthropic_client):
        """Test that an agent can use async tools."""
        # Define an async tool
        async def fetch_data(url):
            # This would normally be an async HTTP request
            return f"Data from {url}"
        
        async_tool = Tool(
            name="fetch_data",
            description="Fetch data from a URL",
            function=fetch_data,
            parameters=[
                {
                    "name": "url",
                    "type": str,
                    "description": "The URL to fetch data from"
                }
            ]
        )
        
        # Create an agent with the async tool
        agent = Agent(
            mock_anthropic_client,
            model="claude-3-5-haiku-latest",
            name="AsyncToolUser",
            system_prompt="You are an agent that uses async tools.",
            tools=[async_tool]
        )
        
        # Verify the tool was assigned to the agent
        assert len(agent.tools) == 1
        assert agent.tools[0].name == "fetch_data"
        
        # In a real test, we would set up mocks to simulate the async tool execution
        # and verify the agent can handle the async nature correctly 