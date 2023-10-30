import os
from langchain.chat_models import AzureChatOpenAI
from typing import List, Dict, Any, Optional
from langchain.schema import Document
from langchain.graphs.graph_document import (
    GraphDocument
)
from langchain.graphs import Neo4jGraph

from langchain.chains.openai_functions import (
    create_openai_fn_chain,
    create_structured_output_chain,
)
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from libs.domainmodels import Property,Node,Relationship,KnowledgeGraph
from libs.utils import map_to_base_node,map_to_base_relationship
import libs.envvars as ENVVars

#os.environ["OPENAI_API_KEY"] = "OPENAI_API_KEY"
#llm = ChatOpenAI(model="gpt-3.5-turbo-16k", temperature=0)



llm = AzureChatOpenAI(
    openai_api_base=ENVVars.ENV_OPENAI_BASE_URL,
    openai_api_version=ENVVars.ENV_OPENAI_API_VERSION,
    deployment_name=ENVVars.ENV_OPENAI_DEPLOYMENT_NAME,
    openai_api_key=ENVVars.ENV_OPENAI_API_KEY,
    openai_api_type="azure"
)



def get_extraction_chain(
    allowed_nodes: Optional[List[str]] = None,
    allowed_rels: Optional[List[str]] = None
    ):
    prompt = ChatPromptTemplate.from_messages(
        [(
          "system",
          f"""# Knowledge Graph Instructions for GPT-4
## 1. Overview
You are a top-tier algorithm designed for extracting information in structured formats to build a knowledge graph.
- **Nodes** represent entities and concepts. They're akin to vehicle parts.
- The aim is to achieve simplicity and clarity in the knowledge graph, making it accessible for a vast audience.
## 2. Labeling Nodes
- **Consistency**: Ensure you use basic or elementary types for node labels.
  - For example, when you identify an entity representing a vehicle, always label it as **"vehicle"**. Avoid using more specific terms like "BMW" or "Lexus".
- **Node IDs**: Never utilize integers as node IDs. Node IDs should be names or human-readable identifiers found in the text.
{'- **Allowed Node Labels:**' + ", ".join(allowed_nodes) if allowed_nodes else ""}
{'- **Allowed Relationship Types**:' + ", ".join(allowed_rels) if allowed_rels else ""}
## 3. Handling Numerical Data and Dates
- Numerical data, like age or other related information, should be incorporated as attributes or properties of the respective nodes.
- **No Separate Nodes for Dates/Numbers**: Do not create separate nodes for dates or numerical values. Always attach them as attributes or properties of nodes.
- **Property Format**: Properties must be in a key-value format.
- **Quotation Marks**: Never use escaped single or double quotes within property values.
- **Naming Convention**: Use camelCase for property keys, e.g., `birthDate`.
## 4. Coreference Resolution
- **Maintain Entity Consistency**: When extracting entities, it's vital to ensure consistency.
If an entity, such as "Vehicle", is mentioned multiple times in the text but is referred to by different names or pronouns (e.g., "Vehicles", "Car"),
always use the most complete identifier for that entity throughout the knowledge graph. In this example, use "Vehicle" as the entity ID.
Remember, the knowledge graph should be coherent and easily understandable, so maintaining consistency in entity references is crucial.
## 5. Strict Compliance
Adhere to the rules strictly. Non-compliance will result in termination.
          """),
            ("human", "Use the given format to extract information from the following input: {input}"),
            ("human", "Tip: Make sure to answer in the correct format"),
        ])
    return create_structured_output_chain(KnowledgeGraph, llm, prompt, verbose=True)


def extract_and_store_graph(
    graph: Neo4jGraph,
    document: Document,
    nodes:Optional[List[str]] = None,
    rels:Optional[List[str]]=None
    ) -> None:
    # Extract graph data using OpenAI functions
    extract_chain = get_extraction_chain(nodes, rels)
    data = extract_chain.run(document.page_content)
    print("\n")
    print("\n")
    print(data)

    # Construct a graph document
    graph_document = GraphDocument(
      nodes = [map_to_base_node(node) for node in data.nodes],
      relationships = [map_to_base_relationship(rel) for rel in data.rels],
      source = document
    )
    # # Store information into a graph
    graph.add_graph_documents([graph_document])