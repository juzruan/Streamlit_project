# %%
import requests
from bs4 import BeautifulSoup
import langchain_text_splitters
import llm_functions 
from openai import OpenAI
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
import streamlit as st


# %% [markdown]
# scrape data from MOM
@st.cache_resource
def scrap_mom_data():
# %%

    def scrape_section(section):
        """Extracts data from a single section."""
        section_data = {}
        
        # title = section.find('h2')
        # section_data['title'] = title.get_text(strip=True) if title else 'No Title Found'

        # # Extract all paragraphs
        # paragraphs = section.find_all('p')
        # section_data['paragraphs'] = [p.get_text(strip=True) for p in paragraphs]

        # # Extract lists
        # list_items = section.find_all('li')
        # section_data['list_items'] = [li.get_text(strip=True) for li in list_items]


        # Extract the title, but only if it's not empty
        title = section.find('h2')
        if title and title.get_text(strip=True):  # Check if the title exists and is non-empty
            section_data['title'] = title.get_text(strip=True)

        # Extract paragraphs, but only if they are not empty
        paragraphs = section.find_all('p')
        paragraph_texts = [p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)]
        if paragraph_texts:  # Only add paragraphs if there are any non-empty ones
            section_data['paragraphs'] = paragraph_texts

        # Extract list items, but only if they are not empty
        list_items = section.find_all('li')
        list_item_texts = [li.get_text(strip=True) for li in list_items if li.get_text(strip=True)]
        if list_item_texts:  # Only add list items if there are any non-empty ones
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
                    if row_data:  # Only add the row if it's not empty
                        table_rows.append(row_data)
                if table_rows:  # Only add the table if it contains valid rows
                    table_data.append(table_rows)

        if table_data:  # Only add tables if they contain non-empty rows
            section_data['tables'] = table_data

        return section_data

    def scrape_page(url):
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses
        
        soup = BeautifulSoup(response.text, 'html.parser')
        data = []

        # Extract all sections with the specified class
        sections = soup.find_all('section', class_='eyd-rte')
        for section in sections:
            section_data = scrape_section(section)
            data.append(section_data)

        return data



    # Get the different links


    platform_workers_main_url = "https://www.mom.gov.sg/employment-practices/platform-workers-act/"


    platform_workers_url = ['what-it-covers','platform-worker','platform-operator','work-injury-compensation-for-platform-workers','cpf-contributions-for-platform-workers','platform-worker-records-and-earning-slips','mandatory-notification-of-platform-operators','platform-work-associations']

    base_url = "https://www.mom.gov.sg/employment-practices/platform-workers-act/"

    # %%
    scrapped_all = {}   
    for platform_workers in  platform_workers_url:
        #scrapped_ = scrape_page(url)
        print(f"Scrapping:{base_url}{platform_workers}")
        scrapped_ = scrape_page(f"{base_url}{platform_workers}")
        scrapped_all[platform_workers] =scrapped_


    scrapped_all


    from langchain_text_splitters import RecursiveJsonSplitter

    splitter = RecursiveJsonSplitter(max_chunk_size=400)

    json_chunks = splitter.split_json(json_data=scrapped_all)

    json_docs = splitter.create_documents(texts=[scrapped_all])
    for chunk in json_chunks:
        print(chunk)


    #from langchain_chroma import Chroma
    from langchain_openai import OpenAIEmbeddings

    embeddings_model = OpenAIEmbeddings(model='text-embedding-3-small')

    vectorstore = FAISS.from_documents(documents=json_docs, embedding=embeddings_model)

    return vectorstore 

prompt = ChatPromptTemplate([ ("human", "You are an assistant for question-answering tasks.\
                                Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know. You can present the findings in a table or in point form. \
Question: {question} \
Context: {context} \
Answer:")])

qa_chain = RetrievalQA.from_chain_type(
    ChatOpenAI(model='gpt-4o-mini', temperature=0), retriever=scrap_mom_data().as_retriever(), chain_type_kwargs={"prompt": prompt}
)

def ask_platform_work_qn(question):
    result = qa_chain.invoke({"query": question})
    return(result["result"])