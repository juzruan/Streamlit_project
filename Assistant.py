# Set up and run this Streamlit App
import streamlit as st

st.set_page_config(
    layout="centered",
    page_title="My Streamlit App"
) 

st.sidebar.write("All the info you need about platform work")
st.sidebar.page_link("Assistant.py", label="Main")
st.sidebar.page_link("AboutMe.py", label="About Me")
st.sidebar.page_link("Methodology.py", label="Methodology")

import llm_functions # <--- This is the helper function that we have created 🆕
import scrape3

# Add some content to the main app
st.title("Platform Work Chatbot 💰🤖")

form = st.form(key="form")

user_prompt = form.text_area("Enter your query regarding platform work here:", height=200)

if form.form_submit_button("Submit"):
    st.toast(f"User Input Submitted - {user_prompt}")
    response = scrape3.ask_platform_work_qn(user_prompt)
    st.write(response) 
    print(f"User Input is {user_prompt}")

with st.expander("IMPORTANT NOTICE"):
    st.write("""

This web application is a prototype developed for educational purposes only. The information provided here is NOT intended for real-world usage and should not be relied upon for making any decisions, especially those related to financial, legal, or healthcare matters.

Furthermore, please be aware that the LLM may generate inaccurate or incorrect information. You assume full responsibility for how you use any generated output.

Always consult with qualified professionals for accurate and personalized advice.

""")
