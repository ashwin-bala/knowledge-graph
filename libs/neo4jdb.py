from langchain.graphs import Neo4jGraph
import libs.envvars as ENVVars

url = ENVVars.ENV_NEODB_URL
username = ENVVars.ENV_NEODB_UNAME
password = ENVVars.ENV_NEODB_PWD

def getDbConnection():
    graph = Neo4jGraph(
        url=url,
        username=username,
        password=password
    )
    return graph


def deleteFromDB(dbConn):
    flag = True
    try:  
        dbConn.query("MATCH (n) DETACH DELETE n")
    except Exception as e: 
        flag = False
        print(e)
    return flag