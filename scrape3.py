import requests
from bs4 import BeautifulSoup
import streamlit as st
from langchain_text_splitters import RecursiveJsonSplitter
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import RetrievalQA
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI
import json

# Scrape data from MOM
# Scrape data from MOM
@st.cache_resource
def scrap_mom_data():
    def scrape_page(url):
        """Scrapes a single page and extracts data."""
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()  # Handle bad responses

        soup = BeautifulSoup(response.text, 'html.parser')
        data = []

        # Extract sections based on specific class
        sections = soup.find_all('div', class_="stikcy-column-container")
        for section in sections:
            data.append(section.get_text(strip=True))  # Get text from each section

        return data

    # List of platform worker URLs to scrape
    base_url = "https://www.mom.gov.sg/employment-practices/platform-workers-act/"
    platform_workers_urls = [
        'what-it-covers', 'platform-worker', 'platform-operator', 
        'work-injury-compensation-for-platform-workers', 'cpf-contributions-for-platform-workers',
        'platform-worker-records-and-earning-slips', 'mandatory-notification-of-platform-operators', 
        'platform-work-associations'
    ]

    # Scrape all pages
    scrapped_all = {}
    for platform_worker_url in platform_workers_urls:
        full_url = f"{base_url}{platform_worker_url}"
        print(f"Scraping: {full_url}")
        scrapped_data = scrape_page(full_url)
        scrapped_all[platform_worker_url] = scrapped_data

    # Check if any of the scraped data is empty
    if not scrapped_all:
        raise ValueError("Scraped data is empty or incomplete.")

    # Flatten the list of scraped text
    flattened_data = []
    for content in scrapped_all.values():
        flattened_data.extend(content)

    # Check if there's any valid text to process
    if not flattened_data:
        raise ValueError("No valid text data to create documents from.")
    
    print(f"Flattened scraped text: {flattened_data}")

    # Split data into manageable chunks
    splitter = RecursiveJsonSplitter(max_chunk_size=400)
    json_chunks = splitter.split_json(json_data={"data": flattened_data})

    # Check if chunks were created correctly
    if not json_chunks or all(not chunk for chunk in json_chunks):
        raise ValueError("Failed to split JSON data into chunks.")

    # Create documents from the chunks
    json_docs = splitter.create_documents(texts=json_chunks)

    # Create a vector store with OpenAI embeddings
    embeddings_model = OpenAIEmbeddings(model='text-embedding-3-small')
    vectorstore = FAISS.from_documents(documents=json_docs, embedding=embeddings_model)

    return vectorstore

# Define QA chain with prompt template
prompt = ChatPromptTemplate([("human", "You are an assistant for question-answering tasks. \
                                Use the following pieces of retrieved context to answer the question. \
                                If you don't know the answer, just say that you don't know. You can present the findings in a table or in point form. \
Question: {question} \
Context: {context} \
Answer:")])

qa_chain = RetrievalQA.from_chain_type(
    ChatOpenAI(model='gpt-4o-mini', temperature=0), retriever=scrap_mom_data().as_retriever(), chain_type_kwargs={"prompt": prompt}
)

def ask_platform_work_qn(question):
    result = qa_chain.invoke({"query": question})
    return(result["result"])