"""
Example of a dynamic delegation architecture using the imagination-engine framework. This implementation 
demonstrates an intelligent executive agent that can either answer simple queries directly or dynamically 
create and delegate complex problems to specialized teams of experts. The system adapts its response strategy 
based on query complexity, demonstrating how agents can optimize resource allocation through contextual 
decision-making and hierarchical collaboration.
"""

import os
from dotenv import load_dotenv
from impossibly import Agent, Graph, Tool, START, END

# Define our recursive graph creation tool
def create_expert_team(query, required_experts, team_task):
    """
    Creates a specialized team of experts based on the requirements and executes their work.
    
    Args:
        query: The original user query to be addressed
        required_experts: Comma-separated list of expert types needed (e.g., "scientist,economist")
        team_task: Description of what the team should accomplish
        
    Returns:
        The final response from the expert team graph
    """
    from openai import AsyncOpenAI
    client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    # Parse the comma-separated list of experts
    expert_list = [expert.strip() for expert in required_experts.split(",")]
    
    # Expert agent definitions
    expert_definitions = {
        "scientist": {
            "name": "Scientist",
            "system_prompt": """
                You are a Scientist Expert Agent. Your role is to analyze problems using empirical data, scientific methodology, and critical reasoning. When you receive a prompt:
                1. Examine the problem from a scientific perspective.
                2. Identify hypotheses and consider experimental evidence.
                3. Explain complex phenomena in simple terms.
                4. Suggest practical experiments or data-driven insights.
                Your response should be analytical, objective, and based on current scientific knowledge.
            """,
            "description": "Scientific expert providing evidence-based analysis"
        },
        "economist": {
            "name": "Economist",
            "system_prompt": """
                You are an Economist Expert Agent. Your role is to evaluate issues through the lens of economic theory and market dynamics. When you receive a prompt:
                1. Analyze the economic implications of the problem.
                2. Consider incentives, costs, and benefits.
                3. Offer insights on policy, market trends, or resource allocation.
                4. Present data or models to support your conclusions.
                Your response should be quantitative where possible and focus on rational economic analysis.
            """,
            "description": "Economic expert analyzing financial and market implications"
        },
        "psychologist": {
            "name": "Psychologist",
            "system_prompt": """
                You are a Psychology Expert Agent. Your role is to understand problems by exploring human behavior, cognitive processes, and emotional factors. When you receive a prompt:
                1. Analyze the emotional or cognitive dimensions of the issue.
                2. Consider motivations, biases, or mental health aspects.
                3. Suggest strategies for behavior change or improved well-being.
                4. Draw on established psychological theories.
                Your response should be empathetic, evidence-based, and practical.
            """,
            "description": "Psychological expert addressing behavioral and cognitive aspects"
        },
        "engineer": {
            "name": "Engineer",
            "system_prompt": """
                You are an Engineering Expert Agent. Your role is to solve problems by applying technical and design principles. When you receive a prompt:
                1. Break down the problem into technical components.
                2. Propose systems, designs, or practical solutions.
                3. Evaluate feasibility and resource requirements.
                4. Use clear technical language and diagrams if needed.
                Your response should be logical, precise, and geared towards implementable solutions.
            """,
            "description": "Engineering expert providing technical solutions"
        },
        "legal_expert": {
            "name": "Legal Expert",
            "system_prompt": """
                You are a Legal Expert Agent. Your role is to analyze issues from a legal and regulatory perspective. When you receive a prompt:
                1. Identify relevant laws, regulations, or legal precedents.
                2. Assess risks and legal implications.
                3. Provide clear advice on compliance or risk mitigation.
                4. Use plain language while ensuring legal accuracy.
                Your response should be cautious, well-informed, and focused on protecting rights and interests.
            """,
            "description": "Legal expert analyzing regulatory and compliance aspects"
        }
    }
    
    # Create the team organizer agent
    team_organizer = Agent(
        client,
        model="gpt-4o",
        name="TeamOrganizer",
        system_prompt=f"""
            You are the Team Organizer for a specialized task. Your role is to:
            1. Clearly define the problem based on the original query
            2. Coordinate the team of experts to address the problem effectively
            3. Ensure each expert contributes their specialized knowledge
            4. Guide the conversation toward a comprehensive solution
            
            Your team's task is: {team_task}
            
            Present the problem clearly to your team and prompt each expert to contribute their unique perspective.
        """,
        description="Coordinates the team of experts and guides them toward a solution"
    )
    
    # Create expert agents based on the required_experts list
    expert_agents = []
    for expert_type in expert_list:
        if expert_type in expert_definitions:
            expert_def = expert_definitions[expert_type]
            expert_agent = Agent(
                client,
                model="gpt-4o",
                name=expert_def["name"],
                system_prompt=expert_def["system_prompt"],
                description=expert_def["description"]
            )
            expert_agents.append(expert_agent)
    
    # Create the team synthesizer agent
    team_synthesizer = Agent(
        client,
        model="gpt-4o",
        name="TeamSynthesizer",
        system_prompt="""
            You are the Team Synthesizer. Your role is to:
            1. Analyze the inputs from all expert team members
            2. Integrate their perspectives into a cohesive solution
            3. Resolve any contradictions or inconsistencies
            4. Produce a comprehensive and actionable response
            
            Your synthesis should be clear, balanced, and reflect the combined expertise of the team.
        """,
        description="Synthesizes the team's insights into a cohesive response",
        shared_memory=expert_agents  # Allow synthesizer to see all expert responses
    )
    
    # Build the expert team graph
    team_graph = Graph()
    team_graph.add_node(team_organizer)
    team_graph.add_node(expert_agents)
    team_graph.add_node(team_synthesizer)
    
    team_graph.add_edge(START, team_organizer)
    team_graph.add_edge(team_organizer, expert_agents)
    team_graph.add_edge(expert_agents, team_synthesizer)
    team_graph.add_edge(team_synthesizer, END)
    
    # Execute the team's analysis - the Graph.invoke method handles async internally
    team_response = team_graph.invoke(f"Original query: {query}\nTeam task: {team_task}")
    return team_response

def __main__():
    # Load environment variables from .env file
    load_dotenv()
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    if not OPENAI_API_KEY:
        raise ValueError("OpenAI API key is not set. Please check your .env file.")

    # Initialize the OpenAI client
    from openai import AsyncOpenAI
    client = AsyncOpenAI(api_key=OPENAI_API_KEY)

    # Create the graph creation tool
    create_expert_team_tool = Tool(
        name="create_expert_team",
        description="Create a specialized team of experts to solve a complex problem. The team will analyze the problem collaboratively and provide a synthesized solution.",
        function=create_expert_team,
        parameters=[
            {
                "name": "query",
                "type": str,
                "description": "The original query or problem to be addressed by the expert team"
            },
            {
                "name": "required_experts",
                "type": str,
                "description": "Comma-separated list of expert types needed (options: scientist, economist, psychologist, engineer, legal_expert)"
            },
            {
                "name": "team_task",
                "type": str,
                "description": "Clear description of what the team should accomplish"
            }
        ]
    )

    # Initialize main executive agent with the ability to create teams
    executive_agent = Agent(
        client, 
        model="gpt-4o", 
        name="ExecutiveAgent", 
        system_prompt="""
            You are an Executive Decision-Making Agent with the ability to delegate complex problems to specialized teams of experts.
            
            When faced with a complex query that requires deep domain knowledge in specific areas, you can:
            1. Analyze the problem to determine which types of experts would be best suited to address it
            2. Create a team of these experts using the create_expert_team tool
            3. Provide the team with a clear task and the original query
            4. Present the team's findings to the user in a clear, actionable format
            
            Expert types available:
            - scientist: For scientific analysis, data interpretation, experimental design
            - economist: For economic implications, market analysis, resource allocation
            - psychologist: For behavioral insights, cognitive aspects, emotional factors
            - engineer: For technical solutions, systems design, practical implementation
            - legal_expert: For regulatory concerns, compliance issues, legal implications
            
            Use this delegation capability for complex, multifaceted problems that benefit from specialized expertise.
            For simple queries, answer directly without creating a team.
        """,
        description="Executive agent that can delegate work to specialized teams",
        tools=[create_expert_team_tool]
    )

    # Initialize and build the main graph
    main_graph = Graph()
    main_graph.add_node(executive_agent)
    main_graph.add_edge(START, executive_agent)
    main_graph.add_edge(executive_agent, END)

    # Example queries to test the recursive architecture
    print("\n=== SIMPLE QUERY (should be answered directly) ===")
    response = main_graph.invoke("What is the capital of France?", show_thinking=True)
    print(f"Response: {response}\n")
    
    print("\n=== COMPLEX QUERY (should delegate to a team) ===")
    response = main_graph.invoke(
        "How might climate change affect global food security in the next 30 years, and what technological and policy solutions could mitigate these impacts?", 
        show_thinking=True
    )
    print(f"Response: {response}")

if __name__ == "__main__":
    __main__() 