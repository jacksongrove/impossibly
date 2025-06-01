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
from impossibly import Agent, Tool, START, END
from impossibly.utils.tools import format_tools_for_api


@pytest.mark.tools
class TestToolFunctionality:
    """Tests for verifying tool functionality."""
    
    @pytest.mark.tools_direct
    def test_tool_direct_execution(self, basic_tools):
        """Test that tools can be executed directly with appropriate parameters."""
        # Get the calculator tool
        calculator = basic_tools[0]
        
        # Execute the tool directly
        result = calculator.execute(a=5, b=3)
        
        # Verify the result
        assert result == 8
    
    @pytest.mark.tools_validation
    def test_tool_parameter_validation(self, basic_tools):
        """Test that tools validate their parameters."""
        # Get the calculator tool
        calculator = basic_tools[0]
        
        # Test with invalid parameter types
        with pytest.raises(TypeError):
            calculator.execute(a="not a number", b=3)
    
    @pytest.mark.tools_error
    def test_tool_error_handling(self, sample_tools):
        """Test that tool errors are handled appropriately."""
        # Get the divider tool
        divider = sample_tools[2]
        
        # Test with a zero denominator
        with pytest.raises(ZeroDivisionError):
            divider.execute(a=10, b=0)
    
    @pytest.mark.tools
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
        assert agent.tools[0].name == "add_numbers"
        assert agent.tools[1].name == "count_words"
        assert agent.tools[2].name == "divide_numbers"
        
        # Mock a simple response from the agent
        with patch.object(agent.client, "invoke", return_value="I would use the add_numbers tool for this."):
            # Invoke the agent with a question that would need tool use
            response = agent.invoke("user", "What is 5 + 3?")
            
            # Just verify we get a response without errors
            assert response == "I would use the add_numbers tool for this."
            
        # Note: Full tool usage testing would require more complex mocking
        # or integration tests with actual services
    
    @pytest.mark.tools
    def test_tool_formatting_for_api(self, basic_tools):
        """Test that tools can be formatted for different LLM APIs."""
        # Format for OpenAI
        openai_tools = format_tools_for_api(basic_tools, api="openai")
        
        # Verify the OpenAI format
        assert len(openai_tools) == 2
        assert openai_tools[0]["type"] == "function"
        assert "function" in openai_tools[0]
        assert "name" in openai_tools[0]["function"]
        assert "description" in openai_tools[0]["function"]
        assert "parameters" in openai_tools[0]["function"]
        
        # Format for Anthropic - expect NotImplementedError
        # TODO: Will be implemented in a future update
        with pytest.raises(NotImplementedError):
            format_tools_for_api(basic_tools, api="anthropic")
    
    @pytest.mark.tools_async
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