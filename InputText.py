import streamlit as st
from langchain.text_splitter import TokenTextSplitter
from langchain.document_loaders import AmazonTextractPDFLoader

import time
import boto3
from fpdf import FPDF
import os
import libs.neo4jdb as neo4dbLibs
import libs.s3upload as s3uploadLibs
import libs.llmhelper as llmHelper
import libs.envvars as ENVVars

# if 'logger' not in st.session_state:
#     logger = logging.getLogger()
#     logger.addHandler(logging.StreamHandler())
#     logger.setLevel(logging.INFO)
#     st.session_state['logger'] = logger
# else:
#     logger = st.session_state['logger']    
    
    
#@st.cache_resource
def getGraphDbConnect():
  graph = neo4dbLibs.getDbConnection()
  return graph

# st = hvcommon.getPageConfig()



# Read the input text
def extractFromRepairManuals(filePath):
    s3FilePath = f"s3://{ENVVars.ENV_S3_FOLDER}/{filePath}"
    print("filePath: ",filePath)    
    textract_client = boto3.client('textract', region_name='us-east-1')
    loader = AmazonTextractPDFLoader(file_path=s3FilePath,client=textract_client)    
    documents = loader.load()
# - in our testing Character split works better with this PDF data set
    text_splitter = TokenTextSplitter(chunk_size=2048, chunk_overlap=24)
    docs = text_splitter.split_documents(documents[:1])
    return docs



def extractAndStore():
    if 'extractAndStore' not in st.session_state:
        with st.status(":blue[Convert PDF to text, Extract Entities and Relationships using LLM and store them into Graph Database ...]", expanded=True) as status:
            st.write("1. Extract text from the PDF Document..")
            time.sleep(2)
            st.write("2. Chunking the text..")
            if 'processPDF' not in st.session_state:
                documents = extractFromRepairManuals("input.pdf")
                st.session_state['processPDF'] = documents
            else:                
               documents = st.session_state['processPDF']
            time.sleep(3)
            st.write("3. Extract Entities and Relationships using Open AI LLM Model..")
            llmHelper.extractAndStoreGraph(documents,getGraphDbConnect())
            time.sleep(2)
            st.write("4. Store the Entities and Relationships as Graph Nodes in Graph Database..")
            time.sleep(1)
            status.update(label=":blue[Entity Extraction and Storage is complete]", state="complete", expanded=False)
            st.session_state['extractAndStore'] = 'yes'





def create_pdf(input_file_path, text_content):
    # save FPDF() class into 
    # a variable pdf
    pdf = FPDF()
    
    # Add a page
    pdf.add_page()
    
    # set style and size of font 
    # that you want in the pdf
    pdf.set_font("Arial", size = 15)
    
    # open the text file in read mode
    f = open(input_file_path, "r")
    
    # insert the texts in pdf
    for x in f:
        pdf.cell(200, 10, txt = x.encode('latin-1', 'ignore').decode('latin-1'), ln = 1, align = 'C')
    
    deleteFiles("input.pdf")
    # save the pdf with name .pdf
    pdf.output("input.pdf") 

def deleteFiles(fileName):
    if os.path.exists(fileName):
        os.remove(fileName)
        time.sleep(5)
    else:
        print("The file does not exist")  



# options = st.multiselect(
#     'Filter only these entities',
#    ["Person", "Company", "Location", "Event", "Movie", "Service", "Award"])

# Query the knowledge graph in a RAG application
form = st.form("my_form")
manualInput = form.text_area(label="Enter your text to identify entities and relationships")
form.form_submit_button("Submit")
if manualInput != '':
    print("Writing the input to text file-started")
    with open("input.txt", "w") as text_file:
        text_file.write(manualInput)
    time.sleep(3)
    print("Writing the input to text file-completed")
    create_pdf("input.txt", manualInput)
    time.sleep(3)
    deleteFiles("input.txt")
    print("Writing the input to PDF file-completed")
    s3uploadLibs.upload_file("input.pdf","hv-ragdemo-training-bucket","input.pdf")
    extractAndStore()          
    print("extracted and store in graphDB")


  


