import os
from dotenv import load_dotenv
from impossibly import Agent, Graph, START, END

def __main__():
    # Load environment variables from .env file
    load_dotenv()
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    if not OPENAI_API_KEY:
        raise ValueError("OpenAI API key is not set. Please check your .env file.")

    # Initialize the OpenAI client
    from openai import OpenAI
    client = OpenAI(api_key=OPENAI_API_KEY)

    # Initialize Agents
    gating_network = Agent(
        client, 
        model="gpt-4o", 
        name="GatingNetwork", 
        system_prompt="""
            You are the Gating Network of an intelligent agent system. Your task is twofold:
            1. Analyze the user's input and decide which specialized agent (e.g., Philosopher, Founder) is best suited to address the query.
            2. Rewrite the original user prompt into a detailed, context-rich instruction tailored to that agent. Include any missing context or clarifying details to ensure the selected agent fully understands the task. Make sure it knows to have a long and thoughtful conversation with the other agent to refine the final response.

            Your response should be clear, succinct, and structured to seamlessly guide and foster a productive conversation between the two agents.
            """,
        description="This agent takes the user's input and decides which agent to pass it to. It then rewrites the user's prompt to be detailed for that specific agent."
    )
    scientist = Agent(
        client, 
        model="gpt-4o", 
        name="Scientist", 
        system_prompt="""
            You are a Scientist Expert Agent. Your role is to analyze problems using empirical data, scientific methodology, and critical reasoning. When you receive a prompt:
            1. Examine the problem from a scientific perspective.
            2. Identify hypotheses and consider experimental evidence.
            3. Explain complex phenomena in simple terms.
            4. Suggest practical experiments or data-driven insights.
            Your response should be analytical, objective, and based on current scientific knowledge.
            """,
        description="This agent is an expert in philosophy and will imagine and expand upon problems in detailed philosophical theory."
    )
    economist = Agent(
        client, 
        model="gpt-4o", 
        name="Economist", 
        system_prompt="""
            You are an Economist Expert Agent. Your role is to evaluate issues through the lens of economic theory and market dynamics. When you receive a prompt:
            1. Analyze the economic implications of the problem.
            2. Consider incentives, costs, and benefits.
            3. Offer insights on policy, market trends, or resource allocation.
            4. Present data or models to support your conclusions.
            Your response should be quantitative where possible and focus on rational economic analysis.
            """,
        description="This agent is an expert in philosophy and will imagine and expand upon problems in detailed philosophical theory."
    )
    psychologist = Agent(
        client, 
        model="gpt-4o", 
        name="Psychologist", 
        system_prompt="""
            You are a Psychology Expert Agent. Your role is to understand problems by exploring human behavior, cognitive processes, and emotional factors. When you receive a prompt:
            1. Analyze the emotional or cognitive dimensions of the issue.
            2. Consider motivations, biases, or mental health aspects.
            3. Suggest strategies for behavior change or improved well-being.
            4. Draw on established psychological theories.
            Your response should be empathetic, evidence-based, and practical.

            """,
        description="This agent is an extremely an critical expert startup founder that is purpose-driven will make clear and critique the issues in a problem."
    )
    historian = Agent(
        client, 
        model="gpt-4o", 
        name="Historian", 
        system_prompt="""
            You are a Historian Expert Agent. Your role is to provide context by drawing on historical knowledge and lessons from past events. When you receive a prompt:
            1. Examine the historical background relevant to the issue.
            2. Identify patterns or parallels with similar past events.
            3. Offer insights into long-term trends and societal impacts.
            4. Ensure your response is well-supported by historical facts.
            Your response should be detailed, contextual, and help users understand the evolution of the problem.
            """,
        description="This agent is an extremely an critical expert startup founder that is purpose-driven will make clear and critique the issues in a problem."
    )
    engineer = Agent(
        client, 
        model="gpt-4o", 
        name="Engineer", 
        system_prompt="""
            You are an Engineering Expert Agent. Your role is to solve problems by applying technical and design principles. When you receive a prompt:
            1. Break down the problem into technical components.
            2. Propose systems, designs, or practical solutions.
            3. Evaluate feasibility and resource requirements.
            4. Use clear technical language and diagrams if needed.
            Your response should be logical, precise, and geared towards implementable solutions.

            """,
        description="This agent is an extremely an critical expert startup founder that is purpose-driven will make clear and critique the issues in a problem."
    )
    legal_expert = Agent(
        client, 
        model="gpt-4o", 
        name="Legal Expert", 
        system_prompt="""
            You are a Legal Expert Agent. Your role is to analyze issues from a legal and regulatory perspective. When you receive a prompt:
            1. Identify relevant laws, regulations, or legal precedents.
            2. Assess risks and legal implications.
            3. Provide clear advice on compliance or risk mitigation.
            4. Use plain language while ensuring legal accuracy.
            Your response should be cautious, well-informed, and focused on protecting rights and interests.
            """,
        description="This agent is an extremely an critical expert startup founder that is purpose-driven will make clear and critique the issues in a problem."
    )
    medical_expert = Agent(
        client, 
        model="gpt-4o", 
        name="Medical Expert", 
        system_prompt="""
            You are a Medical Expert Agent. Your role is to evaluate issues related to health, medicine, and well-being. When you receive a prompt:
            1. Analyze the problem using medical knowledge and clinical best practices.
            2. Suggest evidence-based interventions or lifestyle recommendations.
            3. Consider risks, benefits, and alternative treatments.
            4. Provide clear, empathetic advice without substituting professional medical opinion.
            Your response should be cautious, informative, and prioritize patient safety.

            """,
        description="This agent is an extremely an critical expert startup founder that is purpose-driven will make clear and critique the issues in a problem."
    )
    technology_expert = Agent(
        client, 
        model="gpt-4o", 
        name="Technology Expert", 
        system_prompt="""
            You are a Technology Expert Agent. Your role is to address issues using modern tech trends, software/hardware insights, and digital innovations. When you receive a prompt:
            1. Analyze the technical requirements and challenges.
            2. Consider current and emerging technologies that might solve the problem.
            3. Offer actionable advice on integration, scalability, or optimization.
            4. Use technical language that is clear and accessible.
            Your response should be forward-thinking, practical, and focus on innovative solutions.

            """,
        description="This agent is an extremely an critical expert startup founder that is purpose-driven will make clear and critique the issues in a problem."
    )
    summarizer = Agent(
        client, 
        model="o1", 
        name="Summarizer", 
        system_prompt="""
            You are a Summarizer Agent. Your task is to distill complex or lengthy responses into clear, concise summaries 
            that capture the full nuance of the conversation, including previous messages.

            When you receive a response:
            1. Reformat and condense the content into coherent sentences or paragraphs. This is your default behavior.
            2. Preserve all essential details, nuances, and insights.
            3. Remove redundant or extraneous information while maintaining the original message's intent.
            4. Present the summary in a narrative format without using bullet points.

            Do not reference agent outputs or previous messages explicitly. Speak directly to the user using only the 
            conversation content.

            Your output should be succinct and comprehensive, enabling the user to quickly grasp the core ideas.
            """,
        description="This agent is a summarizer that will make input clear and return it to the user.",
        shared_memory=[scientist, economist, psychologist, historian, engineer, legal_expert, medical_expert, technology_expert]
    )

    # Initialize and build the graph
    graph = Graph()
    graph.add_node(gating_network)
    graph.add_node([scientist, economist, psychologist, historian, engineer, legal_expert, medical_expert, technology_expert])
    graph.add_node(summarizer)

    graph.add_edge(START, gating_network)
    graph.add_edge(gating_network, [scientist, economist, psychologist, historian, engineer, legal_expert, medical_expert, technology_expert])
    graph.add_edge([scientist, economist, psychologist, historian, engineer, legal_expert, medical_expert, technology_expert], summarizer)
    graph.add_edge(summarizer, END)

    # Invoke the graph with an example prompt and show the thinking process
    response = graph.invoke("Tell me how I can live my best life.", show_thinking=True)
    print(response)

if __name__ == "__main__":
    __main__()