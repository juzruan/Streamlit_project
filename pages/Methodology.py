# Set up and run this Streamlit App
import streamlit as st

st.set_page_config(
    layout="centered",
    page_title="Methodology"
) 

st.sidebar.write("All the info you need about platform work")
st.sidebar.page_link("Assistant.py", label="Main")
st.sidebar.page_link("AboutMe.py", label="About Me")
st.sidebar.page_link("Methodology.py", label="Methodology")

# Add some content to the main app
st.title("Platform Work Chatbot 💰🤖")

st.write("""

Project Scope: To develop a chatbot that will use the latest published info on Platform Workers Act to draft responses to enquiries
         
Objectives: To help confused platform work operators and platform workers find important info about the new Platform Workers Act         

Data sources: MOM website

Features: Real-time scrapping of updated info, scalability and low latency, responsive, fast, natural language understanding and processing          
         
""")