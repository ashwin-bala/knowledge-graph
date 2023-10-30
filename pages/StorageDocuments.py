import streamlit as st
from langchain.document_loaders import WikipediaLoader
from langchain.text_splitter import TokenTextSplitter
from langchain.document_loaders import AmazonTextractPDFLoader

import time
import libs.envvars as ENVVars


import boto3
import libs.neo4jdb as neo4dbLibs
import libs.s3upload as s3Upload

@st.cache_resource
def getGraphDbConnect():
  graph = neo4dbLibs.getDbConnection()
  return graph


# Read the wikipedia article
def extractFromWiki():
    raw_documents = WikipediaLoader(query="Walt Disney").load()
    # Define chunking strategy
    text_splitter = TokenTextSplitter(chunk_size=2048, chunk_overlap=24)
    # Only take the first the raw_documents
    documents = text_splitter.split_documents(raw_documents[:1])
    print(documents)

#extractFromWiki()



# Read the PDF document
@st.cache_data(show_spinner="Reading and Chunking the document")
def extractFromRepairManuals(s3FilePath):
    print("s3FilePath: ",s3FilePath)    
    textract_client = boto3.client('textract', region_name='us-east-1')
    loader = AmazonTextractPDFLoader(file_path=s3FilePath,client=textract_client)    
    documents = loader.load()
    text_splitter = TokenTextSplitter(chunk_size=2048, chunk_overlap=24)
    docs = text_splitter.split_documents(documents[:1])
    print("Complete creating text documents from PDF")
    return docs


s3FilePath = f"s3://{ENVVars.ENV_S3_FOLDER}/Crawfords_Auto_Repair_Guide-gen-maintenance-only-5pgs.pdf"


def extractAndStore(getGraphDbConnect, extractAndStoreGraph):
    if 'extractAndStore' not in st.session_state:
        with st.status(":blue[Convert PDF to text, Extract Entities and Relationships using LLM and store them into Graph Database ...]", expanded=True) as status:
            st.write("1. Extract text from the PDF Document..")
            time.sleep(2)
            st.write("2. Chunking the text..")
            if 'processPDF' not in st.session_state:
                documents = extractFromRepairManuals(s3FilePath)
                st.session_state['processPDF'] = documents
            else:                
               documents = st.session_state['processPDF']
            time.sleep(3)
            st.write("3. Extract Entities and Relationships using Open AI LLM Model..")
            extractAndStoreGraph(documents,getGraphDbConnect())
            time.sleep(2)
            st.write("4. Store the Entities and Relationships as Graph Nodes in Graph Database..")
            time.sleep(1)
            status.update(label=":blue[Entity Extraction and Storage is complete]", state="complete", expanded=False)
            st.session_state['extractAndStore'] = 'yes'


# Query the knowledge graph in a RAG application

lst = s3Upload.list_files(ENVVars.ENV_S3_FOLDER)
st.header("Reading the document from S3 bucket")
option = st.selectbox(
    "Please find the files in bucket",
    lst
)
#extractAndStore(getGraphDbConnect, extractAndStoreGraph)            



