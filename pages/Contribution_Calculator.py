# Set up and run this Streamlit App
import streamlit as st

st.set_page_config(
    layout="centered",
    page_title="CPF Contribution Calculator"
) 

st.sidebar.write("All the info you need about platform work")

# Add some content to the main app
st.title("Platform Work Chatbot 💰🤖")

Age = st.number_input("Your age, as at 1 January of the year, is: ")

GE = st.number_input("Your gross earnings for the year is: $")

FEDA = st.radio(
    "What is your mode of transport?",
    ["Cars, vans, lorries, trucks", "Motorcycles, power-assisted bicycles, motorised personal mobility devices", "Bicycles, on foot (including use of public transport)","None"],

if FEDA == "Cars, vans, lorries, trucks":
    st.write("Your Fixed Expense Deduction Amount is 60%.")
    FEDAr == 0.6
else:
    FEDA == "Motorcycles, power-assisted bicycles, motorised personal mobility devices":
    st.write("Your Fixed Expense Deduction Amount is 35%.")
    FEDAr == 0.35
else:
    FEDA == "Bicycles, on foot (including use of public transport)":
    st.write("Your Fixed Expense Deduction Amount is 20%.")
    FEDAr == 0.2
else:
    FEDAr == 0

