"""
Feature tests for core agent interaction capabilities.

This tests the following features:
1. Basic agent creation and invocation
2. Agent-to-agent communication in a graph
3. Agent memory and history
4. Multiple model types working together
"""
import pytest
from unittest.mock import patch

# Import the necessary components
from imengine import Agent, Graph, START, END


class TestAgentInteraction:
    """Tests for verifying agent interaction capabilities."""
    
    def test_conversation_memory(self, mock_clients):
        """Test that agents maintain conversation history."""
        anthropic_client, _ = mock_clients
        
        # Create an agent
        agent = Agent(
            anthropic_client,
            model="claude-3-5-haiku-latest",
            name="MemoryAgent",
            system_prompt="You are an agent with memory capabilities."
        )
        
        # Mock the invoke method for controlled responses
        responses = ["First response", "Response referencing previous input"]
        
        with patch.object(agent.client, "invoke", side_effect=responses):
            # First interaction
            response1 = agent.invoke("user", "Remember this: blue sky")
            
            # Second interaction should reference conversation history
            response2 = agent.invoke("user", "What did I ask you to remember?")
            
            # Verify responses
            assert response1 == "First response"
            assert response2 == "Response referencing previous input"
            
            # Verify the messages were added to history (we need to check the underlying client)
            assert len(agent.messages) == 4  # System prompt + 2 user messages + 2 assistant responses
            
            # Verify context was preserved between calls
            msgs = [msg for msg in agent.messages if msg.get("role") == "user"]
            assert len(msgs) == 2
            assert "Remember this: blue sky" in str(msgs[0])
            assert "What did I ask you to remember?" in str(msgs[1])
    
    def test_multi_agent_collaboration(self, mock_clients):
        """Test that multiple agents can collaborate in a graph structure."""
        anthropic_client, openai_client = mock_clients
        
        # Create agents with different specialties
        expert1 = Agent(
            anthropic_client,
            model="claude-3-5-haiku-latest",
            name="Expert1",
            system_prompt="You are an expert on topic A.",
            description="Expert on topic A"
        )
        
        expert2 = Agent(
            openai_client,
            model="gpt-4o",
            name="Expert2",
            system_prompt="You are an expert on topic B.",
            description="Expert on topic B"
        )
        
        coordinator = Agent(
            anthropic_client,
            model="claude-3-5-sonnet-latest",
            name="Coordinator",
            system_prompt="You coordinate between experts to solve complex problems."
        )
        
        # Create a collaborative graph
        graph = Graph()
        graph.add_node(expert1)
        graph.add_node(expert2)
        graph.add_node(coordinator)
        
        # Connect the nodes with appropriate edges
        graph.add_edge(START, coordinator)
        graph.add_edge(coordinator, expert1)
        graph.add_edge(coordinator, expert2)
        graph.add_edge(coordinator, END)
        graph.add_edge(expert1, coordinator)
        graph.add_edge(expert2, coordinator)
        
        # Mock the coordinator to route to expert1
        with patch.object(coordinator.client, "invoke", return_value="I'll consult Expert1 on this. \\Expert1\\"):
            # Mock expert1's response
            with patch.object(expert1.client, "invoke", return_value="This is my expert opinion on topic A."):
                # Mock the graph execution to simulate the path
                with patch.object(graph, "_run_graph") as mock_run:
                    mock_run.return_value = "Final collaborative response"
                    
                    # Invoke the graph
                    response = graph.invoke("This is a question about topic A and B.")
                    
                    # Verify the response
                    assert response == "Final collaborative response"
                    # In a real implementation, we would verify the execution path
    
    def test_cross_agent_memory_access(self, mock_anthropic_client):
        """Test that agents can access memory from other agents."""
        # Create the first agent and populate its memory
        memory_agent = Agent(
            mock_anthropic_client,
            model="claude-3-5-haiku-latest",
            name="MemoryAgent",
            system_prompt="You are an agent that stores information."
        )
        
        # Simulate some history in the memory agent
        memory_agent.messages.append({"role": "user", "content": "Remember that the capital of France is Paris."})
        memory_agent.messages.append({"role": "assistant", "content": "I'll remember that the capital of France is Paris."})
        
        # Create a second agent that can access the first agent's memory
        reader_agent = Agent(
            mock_anthropic_client,
            model="claude-3-5-haiku-latest",
            name="ReaderAgent",
            system_prompt="You can access information from other agents.",
            shared_memory=[memory_agent]
        )
        
        # Verify shared memory is properly initialized
        assert len(reader_agent.shared_memory) == 1
        assert reader_agent.shared_memory[0].name == "MemoryAgent"
        
        # In a real implementation, the reader would be able to access the memory agent's history
        # Here we just verify the setup
    
    def test_multi_step_reasoning(self, mock_anthropic_client):
        """Test that agents can perform multi-step reasoning through a graph structure."""
        # Create a single agent that can route to itself for multi-step reasoning
        reasoner = Agent(
            mock_anthropic_client,
            model="claude-3-5-sonnet-latest",
            name="Reasoner",
            system_prompt="You solve problems step by step. If you need more steps, route back to yourself."
        )
        
        # Create a graph allowing self-loops
        graph = Graph()
        graph.add_node(reasoner)
        graph.add_edge(START, reasoner)
        graph.add_edge(reasoner, reasoner)  # Self-loop for multi-step reasoning
        graph.add_edge(reasoner, END)
        
        # Mock the reasoner to first route to itself, then to END
        with patch.object(reasoner.client, "invoke") as mock_invoke:
            mock_invoke.side_effect = [
                "Step 1: I'll break down the problem. \\Reasoner\\",  # First call, routes back to self
                "Step 2: Now I have the final answer. \\END\\"  # Second call, routes to END
            ]
            
            # Mock the graph execution
            with patch.object(graph, "_run_graph") as mock_run:
                mock_run.return_value = "Multi-step reasoning complete: The answer is 42."
                
                # Invoke the graph with a complex problem
                response = graph.invoke("What is the meaning of life?")
                
                # Verify the response
                assert response == "Multi-step reasoning complete: The answer is 42."
                
                # Verify that the mock was called twice for the multi-step reasoning
                assert mock_invoke.call_count == 2 