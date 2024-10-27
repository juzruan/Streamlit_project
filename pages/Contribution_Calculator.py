# Set up and run this Streamlit App
import streamlit as st
import llm_functions
import openai
import pandas as pd

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

try:
    total_cpf_con = reference_df.loc[reference_df['Total_CPF_Con'] == 'Total CPF Contribution', 'Value'].values[0]
    platform_worker_share = reference_df.loc[reference_df['PW_Share_CPF_Con'] == 'Platform Worker Share of CPF Contribution', 'Value'].values[0]
except IndexError:
    st.error("Required fields not found in reference data.")
    st.stop()

# Display result if inputs are filled
if Age and NE and Year:
    result = calculate_with_llm(Age, NE, Year, Total_CPF_Con, PW_Share_CPF_Con)
    st.write("Calculation Results:", result)
else:
    st.write("Please enter all required fields.")
