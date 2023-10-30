import streamlit as st


import libs.neo4jdb as neo4dbLibs

@st.cache_resource
def getGraphDbConnect():
  graph = neo4dbLibs.getDbConnection()
  return graph


if 'clicked' not in st.session_state:
    st.session_state.clicked = False

def click_button():
    st.session_state.clicked = True

st.button('Delete data in graphDB', key='delete' ,on_click=click_button)

if st.session_state.clicked:
    # The message and nested widget will remain on the page
    # Delete the graph
    flag = neo4dbLibs.deleteFromDB(getGraphDbConnect())
    if flag:
        st.success('Data deleted in graphDB!', icon="✅")
    else:
        st.error('Data was not deleted in graphDB', icon="🚨")