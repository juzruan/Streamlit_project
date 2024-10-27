# Set up and run this Streamlit App
import streamlit as st
import llm_functions
import openai
import pandas as pd
from langchain.chains import RetrievalQA
from langchain.prompts import ChatPromptTemplate
from langchain.chat_models import ChatOpenAI

st.set_page_config(
    layout="centered",
    page_title="CPF Contribution Calculator"
) 

st.sidebar.write("All the info you need about platform work")

# Add some content to the main app
st.title("Platform Work Chatbot 💰🤖")

st.write("This calculator is for Platform Workers born in or after 1995, or those who opt in to increased CPF savings.")

Year = st.number_input("You are computing CPF contributions for income earned in Year: ", min_value=2025,max_value=2029,step=1)

Age = st.number_input("Your age, as at 1 January of the year, is: ", min_value=1,max_value=99,step=1)

GE = st.number_input("Your gross earnings for the year is: $",min_value=1,step=1)

FEDA = st.radio(
    "What is your mode of transport?",
    ["Cars, vans, lorries, trucks", "Motorcycles, power-assisted bicycles, motorised personal mobility devices", "Bicycles, on foot (including use of public transport)","None"])

if FEDA == "Cars, vans, lorries, trucks":
    st.write("Your Fixed Expense Deduction Amount is 60%.")
    FEDAr = 0.6
elif FEDA == "Motorcycles, power-assisted bicycles, motorised personal mobility devices":
    st.write("Your Fixed Expense Deduction Amount is 35%.")
    FEDAr = 0.35
elif FEDA == "Bicycles, on foot (including use of public transport)":
    st.write("Your Fixed Expense Deduction Amount is 20%.")
    FEDAr = 0.2
else:
    FEDAr = 0

NE = (1-FEDAr)*GE
st.write(f"Your Net Earnings is ${NE:.2f}.")

# Load the reference data CSV
csv_file_path = "https://raw.githubusercontent.com/juzruan/Streamlit_project/refs/heads/main/ConRate.csv"  # update this path
reference_df = pd.read_csv(csv_file_path)

# Define CPF calculation prompt template
cpf_prompt = ChatPromptTemplate([("human", "You are an assistant to calculate CPF contributions. \
Use the following details and reference data to compute: \
- Total CPF contributions \
- Platform worker's share of contributions \
If you can't determine contributions, state 'Calculation unavailable'. \
Details: \
Net Earnings: {NE} \
Age: {Age} \
Year: {Year} \
Reference Data: {reference_data}")])

# Define the LLM chain with the prompt template
cpf_chain = LLMChain(
    llm=ChatOpenAI(model='gpt-4o-mini', temperature=0),
    prompt=cpf_prompt
)

def calculate_cpf_contributions(NE, Age, Year, reference_df):
    # Convert reference data to a dictionary format for the prompt
    reference_data = reference_df.to_dict()
    
    # Prepare the input data for the LLM chain
    inputs = {
        "NE": NE,
        "Age": Age,
        "Year": Year,
        "reference_data": reference_data
    }
    
    # Run the chain to get the result
    result = cpf_chain.run(inputs)
    return result

# Calculate CPF contributions
cpf_result = calculate_cpf_contributions(NE, Age, Year, reference_df)

# Display results in Streamlit
st.write("CPF Contribution Calculation:", cpf_result)
