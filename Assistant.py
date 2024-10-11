# Set up and run this Streamlit App
import streamlit as st
import llm_functions # <--- This is the helper function that we have created 🆕
import scrape

st.set_page_config(
    layout="centered",
    page_title="My Streamlit App"
)

mbs_otters_path = "pictures/mbs_otters.png"  
iras_logo_path = "pictures/iras logo.png"  

st.sidebar.write("Your personal income tax relief calculator")

# Display the logo at the top of the sidebar
st.sidebar.image(iras_logo_path, use_column_width=True)  # `use_column_width` makes the logo fit the sidebar's width
st.sidebar.image(mbs_otters_path, use_column_width=True)  # `use_column_width` makes the logo fit the sidebar's width

# Add some content to the main app
st.title("Tax Relief Chatbot 💰🤖")

form = st.form(key="form")

user_prompt = form.text_area("Enter your query regarding personal income tax relief here:", height=200)

if form.form_submit_button("Submit"):
    st.toast(f"User Input Submitted - {user_prompt}")
    response = prep_data1.ask_tax_relief_qn(user_prompt)
    st.write(response) 
    print(f"User Input is {user_prompt}")

with st.expander("IMPORTANT NOTICE"):
    st.write("""

This web application is a prototype developed for educational purposes only. The information provided here is NOT intended for real-world usage and should not be relied upon for making any decisions, especially those related to financial, legal, or healthcare matters.

Furthermore, please be aware that the LLM may generate inaccurate or incorrect information. You assume full responsibility for how you use any generated output.

Always consult with qualified professionals for accurate and personalized advice.

""")
