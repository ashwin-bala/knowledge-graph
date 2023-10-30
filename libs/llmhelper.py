from langchain.chains import GraphCypherQAChain
from langchain.chat_models import AzureChatOpenAI
from stqdm import stqdm
import libs.extractstoragegraph as graphMod
import libs.envvars as ENVVars


def getLLM():
    llm = AzureChatOpenAI(  
                openai_api_base=ENVVars.ENV_OPENAI_BASE_URL,
                openai_api_version=ENVVars.ENV_OPENAI_API_VERSION,
                deployment_name=ENVVars.ENV_OPENAI_DEPLOYMENT_NAME,
                openai_api_key=ENVVars.ENV_OPENAI_API_KEY,
                openai_api_type="azure"
        )        
    return llm 

def graphChain(graph):
    llm = getLLM() 
    graph.refresh_schema()

    cypher_chain = GraphCypherQAChain.from_llm(
        graph=graph,
        cypher_llm=llm,
        qa_llm=llm,
        validate_cypher=True, # Validate relationship directions
        verbose=True
    )
        
    return cypher_chain 

def extractAndStoreGraph(documents,graph):
    for i, d in stqdm(enumerate(documents), total=len(documents)):
       graphMod.extract_and_store_graph(graph,d)