'''
Define individual agent types to be called within the graph structure.
'''
import os
from dotenv import load_dotenv
from openai import OpenAI

def agent(client, system_prompt="You are a helpful assistant.", chat_prompt=None):
    completion = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": chat_prompt
            }
        ]
    )

    return completion.choices[0].message

def __main__():
    # Load environment variables
    load_dotenv()
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    if not OPENAI_API_KEY:
        raise ValueError("API key is not set. Please check your environment variables or .env file.")

    # Initalize client
    client = OpenAI(api_key=OPENAI_API_KEY)

    # Call agent
    response = agent(client, "You are a helpful assistant.", "Write a haiku about recursion in programming.").content
    print(response)
    


if __name__ == "__main__":
    __main__()