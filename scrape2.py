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
@st.cache_resource
def scrap_mom_data():

    def scrape_section(section):
        """Extracts data from a single section."""
        section_data = {}
        
        # Extract title, paragraphs, lists, and tables if they exist
        title = section.find('h2')
        if title and title.get_text(strip=True):
            section_data['title'] = title.get_text(strip=True)

        paragraphs = section.find_all('p')
        paragraph_texts = [p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)]
        if paragraph_texts:
            section_data['paragraphs'] = paragraph_texts

        list_items = section.find_all('li')
        list_item_texts = [li.get_text(strip=True) for li in list_items if li.get_text(strip=True)]
        if list_item_texts:
            section_data['list_items'] = list_item_texts

        tables = section.find_all('table')
        table_data = []
        for table in tables:
            rows = table.find_all('tr')
            if rows:
                table_rows = []
                for row in rows:
                    columns = row.find_all(['td', 'th'])
                    row_data = [col.get_text(strip=True) for col in columns if col.get_text(strip=True)]
                    if row_data:
                        table_rows.append(row_data)
                if table_rows:
                    table_data.append(table_rows)

        if table_data:
            section_data['tables'] = table_data

        return section_data

    def scrape_page(url):
        """Scrapes a single page and extracts data."""
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()  # Handle bad responses

        soup = BeautifulSoup(response.text, 'html.parser')
        data = []

        # Extract sections based on specific class (adjust based on actual class used)
        sections = soup.find_all('section', class_='eyd-rte')
        for section in sections:
            section_data = scrape_section(section)
            if section_data:  # Only add if there's content
                data.append(section_data)

        return data

    # List of platform worker URLs to scrape
    base_url = "https://www.mom.gov.sg/employment-practices/platform-workers-act/"
    platform_workers_urls = ['what-it-covers', 'platform-worker', 'platform-operator', 
                             'work-injury-compensation-for-platform-workers', 'cpf-contributions-for-platform-workers',
                             'platform-worker-records-and-earning-slips', 'mandatory-notification-of-platform-operators', 
                             'platform-work-associations']

        # Scrape all pages
    scrapped_all = {}
    for platform_worker_url in platform_workers_urls:
        full_url = f"{base_url}{platform_worker_url}"
        print(f"Scraping: {full_url}")
        scrapped_data = scrape_page(full_url)
        scrapped_all[platform_worker_url] = scrapped_data
    for key in scrapped_all:
        print(key)

    # Check if any of the scraped data is empty
    if not scrapped_all:
        raise ValueError("Scraped data is empty or incomplete.")

    # Convert the scraped data into text
    scrapped_text = [json.dumps(scrapped_all[section]) for section in scrapped_all]

    # Check if there's any valid text to process
    if not scrapped_text or all(not text for text in scrapped_text):
        raise ValueError("No valid text data to create documents from.")
    
    print(f"Scrapped text: {scrapped_text}")

    # Split data into manageable chunks
    splitter = RecursiveJsonSplitter(max_chunk_size=400)
    json_chunks = splitter.split_json(json_data=scrapped_all)
    
    # Check if chunks were created correctly
    if not json_chunks or all(not chunk for chunk in json_chunks):
        raise ValueError("Failed to split JSON data into chunks.")
    
    json_docs = splitter.create_documents(texts=scrapped_text)

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
    ChatOpenAI(model='gpt-4o-mini', temperature=0),
    retriever=scrap_mom_data().as_retriever(),
    chain_type_kwargs={"prompt": prompt}
)

# Function to ask platform worker questions
def ask_platform_work_qn(question):
    # Manually retrieve documents using the retriever
    retriever = scrap_mom_data().as_retriever()

    # Use invoke method instead of the deprecated get_relevant_documents
    retrieved_docs = retriever.invoke({"query": question})

    # Combine the content of retrieved documents into the context
    context = " ".join([doc.page_content for doc in retrieved_docs])

    # Debug: Print the context to check if it contains meaningful information
    print(f"Context for the QA Chain: {context}")
    
    # Check if the context is empty or too short (potential problem)
    if not context.strip():
        print("Warning: Empty context retrieved. This might be why the answer is 'I don't know'.")
    
    # Now invoke the QA chain with the retrieved context
    result = qa_chain.invoke({"query": question})
    
    return result["result"]