Quickstart
==========

This guide will help you get started with Impossibly. It covers the basic concepts and provides examples of how to create agents and connect them in graphs.

Basic Usage
-----------

Let's start with a simple example of creating an agent and using it:

.. code-block:: python

    import os
    from openai import OpenAI
    from impossibly import Agent

    # Initialize an OpenAI client
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

    # Create an agent
    agent = Agent(
        client=client,
        model="gpt-4o",
        name="research_agent",
        system_prompt="You are a helpful research assistant."
    )

    # Invoke the agent
    response = agent.invoke("user", "What is reinforcement learning?")
    print(response)

Creating a Graph of Agents
--------------------------

The real power of Impossibly comes from connecting multiple agents in a graph:

.. code-block:: python

    from openai import OpenAI
    from impossibly import Agent, Graph
    from impossibly.utils.start_end import START, END

    # Initialize OpenAI client
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

    # Create agents with different specializations
    researcher = Agent(
        client=client,
        model="gpt-4o",
        name="researcher",
        system_prompt="You are a research agent that finds information. Keep responses brief and factual."
    )

    writer = Agent(
        client=client,
        model="gpt-4o",
        name="writer",
        system_prompt="You are a writing agent that can rewrite text to be more clear and engaging."
    )

    # Create a graph and add the agents
    graph = Graph()
    graph.add_node([researcher, writer])

    # Create connections between agents
    graph.add_edge(START, researcher)
    graph.add_edge(researcher, writer)
    graph.add_edge(writer, END)

    # Execute the graph with an initial user query
    result = graph.invoke("Explain quantum computing in simple terms.")
    print(result)

Using Tools with Agents
-----------------------

You can enhance agents with tools to interact with external systems:

.. code-block:: python

    from impossibly import Agent
    from impossibly.utils.tools import Tool
    from openai import OpenAI
    import requests

    # Define a tool to fetch weather data
    def get_weather(location):
        """
        Get the current weather for a location.
        
        Args:
            location (str): The city name to get weather for
            
        Returns:
            dict: Weather information
        """
        # Example API call (you would use a real weather API)
        return {"location": location, "temperature": "72°F", "condition": "Sunny"}
    
    # Create a tool
    weather_tool = Tool(
        name="get_weather",
        function=get_weather,
        description="Get the current weather for a location",
        parameters={
            "location": {
                "type": "string",
                "description": "The city name to get weather for"
            }
        }
    )
    
    # Initialize client and create agent with the tool
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    
    weather_agent = Agent(
        client=client,
        model="gpt-4o",
        name="weather_agent",
        system_prompt="You are a helpful assistant that provides weather information.",
        tools=[weather_tool]
    )
    
    # Invoke the agent with a query that will use the tool
    response = weather_agent.invoke("user", "What's the weather like in San Francisco?")
    print(response)

Next Steps
----------

Now that you've seen the basics, check out the following guides:

- :doc:`api/agent`: Learn more about creating and customizing agents
- :doc:`api/graph`: Discover how to build more complex agent workflows
- :doc:`api/utils`: Understand how to create and use tools
- :doc:`contributing`: See how to contribute to the project 