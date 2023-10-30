import streamlit as st
from libs.llmhelper import graphChain
import libs.neo4jdb as neo4dbLibs

@st.cache_resource
def getGraphDbConnect():
  graph = neo4dbLibs.getDbConnection()
  return graph

# Create a text box to ask question
form2 = st.form("my_form2")
inpt = form2.text_area("Enter your query text:")
form2.form_submit_button("Submit")

# Submit the question to a server
if inpt != '':
    cypher_chain = graphChain(getGraphDbConnect())
    st.write(cypher_chain.run(inpt))

