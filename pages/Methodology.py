# Set up and run this Streamlit App
import streamlit as st

st.set_page_config(
    layout="centered",
    page_title="Methodology"
) 

st.sidebar.write("All the info you need about platform work")

# Add some content to the main app
st.title("Platform Work Chatbot 💰🤖")

st.image("pages/image.png", caption="Methodology", use_column_width=True)
