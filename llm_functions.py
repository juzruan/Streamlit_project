import os
from dotenv import load_dotenv
import openai
import tiktoken
import streamlit as st

# Load environment variables from .env file
#load_dotenv('.env')

# Set the API key for the OpenAI client
#openai.api_key = os.getenv('OPENAI_API_KEY')
#client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

OPENAI_API_KEY=st.secrets["OPENAI_API_KEY"]

def get_embedding(input, model='text-embedding-3-small'):
    response = client.embeddings.create(
        input=input,
        model=model
    )
    return [x.embedding for x in response.data]


# This is the "Updated" helper function for calling LLM
def get_completion(prompt, model="gpt-4o-mini",temperature=0, top_p=1.0, max_tokens=1024, n=1, json_output=False):
    if json_output == True:
      output_json_structure = {"type": "json_object"}
    else:
      output_json_structure = None

    messages = [{"role": "user", "content": prompt}]
    response = client.chat.completions.create( #originally was openai.chat.completions
        model=model,
        messages=messages,
        temperature=temperature,
        top_p=top_p,
        max_tokens=max_tokens,
        n=1,
        response_format=output_json_structure,
    )
    return response.choices[0].message.content


# Note that this function directly take in "messages" as the parameter.
def get_completion_by_messages(messages, model="gpt-4o-mini", temperature=0, top_p=1.0, max_tokens=1024, n=1):
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        top_p=top_p,
        max_tokens=max_tokens,
        n=1
    )
    return response.choices[0].message.content


# This function is for calculating the tokens given the "message"
# ⚠️ This is simplified implementation that is good enough for a rough estimation
def count_tokens(text):
    encoding = tiktoken.encoding_for_model("gpt-4o-mini",)
    return len(encoding.encode(text))


def count_tokens_from_message(messages):
    encoding = tiktoken.encoding_for_model("gpt-4o-mini",)
    value = ' '.join([x.get('content') for x in messages])
    return len(encoding.encode(value))

# This function is for computing the total CPF Contributions and the Platform Worker's share of CPF contributions.

def calculate_with_llm(age, NE, year, reference_df):
    # Convert user inputs to the appropriate data types if needed
    age = int(age) if age else None
    NE = int(NE) if NE else None
    year = int(year) if year else None
    
    # Convert the DataFrame to a dictionary for reference
    reference_data = reference_df.to_dict(orient="records")
    
    # Create a prompt with user inputs and reference data
    prompt = (
        f"Using the following information:\n"
        f"Age: {age}\n"
        f"Net Earnings (NE): {NE}\n"
        f"Year: {year}\n"
        f"Reference data: {reference_data}\n\n"
        "Please calculate the amount based on the above information."
    )
    
    # Send prompt to OpenAI
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=100  # Adjust tokens based on expected response length
    )
    
    # Extract the answer
    answer = response.choices[0].text.strip()
    return answer
