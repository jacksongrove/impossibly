import os
import sys
from dotenv import load_dotenv
from imagination_engine import Agent, Graph, START, END

def __main__():
    # Load environment variables from .env file
    load_dotenv()
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    if not OPENAI_API_KEY:
        raise ValueError("OpenAI API key is not set. Please check your .env file.")

    # Initialize the OpenAI client
    from openai import AsyncOpenAI
    client = AsyncOpenAI(api_key=OPENAI_API_KEY)

    # Initialize a single agent focused on architecture
    architecture_agent = Agent(
        client, 
        model="gpt-4o", 
        name="ArchitectureExpert", 
        system_prompt="""
            You are an expert in architecture with deep knowledge of both historical and modern architectural styles.
            When discussing architecture, focus on:
            1. The historical context and cultural significance
            2. Key design elements and their purposes
            3. Notable examples and their impact
            4. The relationship between form and function
            5. How the architecture reflects the values and needs of its time
            
            Provide detailed, engaging descriptions that help the listener visualize the structures and understand their importance.
            """,
        description="An expert agent that provides detailed insights about architectural styles, buildings, and design principles."
    )

    # Initialize and build the graph with streaming enabled
    graph = Graph(streaming=True)
    graph.add_node(architecture_agent)

    # Create a simple path: START -> ArchitectureExpert -> END
    graph.add_edge(START, architecture_agent)
    graph.add_edge(architecture_agent, END)
    
    # For async usage:
    import asyncio
    
    async def stream_response():
        print("\n" + "-" * 50)
        try:
            stream = await graph.invoke("Tell me about the most fascinating architectural marvels from ancient civilizations.")
            
            if isinstance(stream, str):
                print("Not streaming, got full response at once.")
                print(stream)
            else:
                print("Streaming response in real-time:")
                async for chunk in stream:
                    print(chunk, end="", flush=True)
        except Exception as e:
            print(f"Error during streaming: {str(e)}")
            import traceback
            traceback.print_exc()
        
        print("\n" + "-" * 50)
        print("Complete!")

    # Run the async function
    asyncio.run(stream_response())

if __name__ == "__main__":
    __main__() 