import json, re, os
from hdbcli import dbapi
from gen_ai_hub.proxy.langchain.init_models import init_embedding_model
from gen_ai_hub.proxy import GenAIHubProxyClient
from gen_ai_hub.proxy.langchain.amazon import ChatBedrock
from langchain.schema import AIMessage, HumanMessage, SystemMessage

def replace_where_clause(query, replacement):
    for key, value in replacement.items():
        # Create regex pattern to find the clause to replace
        pattern = rf"({key}\s*=\s*')[^']*(')"
        replacement_string = rf"\1{value}\2"

        # Perform the replacement
        query = re.sub(pattern, replacement_string, query)

    return query

HANA_DB_ADDRESS = "HANA_DB_ADDRESS"
HANA_DB_PORT = "HANA_DB_PORT"
HANA_DB_USER = "HANA_DB_USER"
HANA_DB_PASSWORD ="HANA_DB_PASSWORD"

os.environ["AICORE_CLIENT_ID"] = "AICORE_CLIENT_ID"
os.environ["AICORE_CLIENT_SECRET"] = "AICORE_CLIENT_SECRET"
os.environ["AICORE_AUTH_URL"] = "AICORE_AUTH_URL"
os.environ["AICORE_BASE_URL"] = "AICORE_BASE_URL"
os.environ["AICORE_RESOURCE_GROUP"] = "AICORE_RESOURCE_GROUP"

gen_ai_hub_proxy_client = GenAIHubProxyClient(
    base_url="AICORE_BASE_URL",
    auth_url="AICORE_AUTH_URL",
    client_id="AICORE_CLIENT_ID",
    client_secret="AICORE_CLIENT_SECRET",
    resource_group="AICORE_RESOURCE_GROUP"
)
 
driver = dbapi.connect(
    address=HANA_DB_ADDRESS, 
    port=HANA_DB_PORT, 
    user=HANA_DB_USER, 
    password=HANA_DB_PASSWORD
)

chat_model = ChatBedrock(proxy_client=gen_ai_hub_proxy_client,
                        model_name= "anthropic--claude-3.5-sonnet"
                                     )

cursor = driver.cursor()
schema = """[
                { Node:  
                [  
                { name:NODE_TYPE, data_type: STRING }
                { name:DESCRIPTION, data_type: STRING } ,   
                { name:NODE_ID, data_type: STRING }    
                predefined list of NODE_TYPE:[ 
                                    Customer, 
                                    Order,
                                    Product, 
                                    Category,   
                                    Supplier
                                    ]
                ]   
                }
                ]

                Relationships: 
                [ 
                { CUSTOMER_PLACES_ORDER: [ source: Node(NODE_TYPE: Customer), destination: Node(NODE_TYPE: Order) ], description : ' Customer places one or many orders '}, 
                { ORDER_ASSOCIATED_TO_CUSTOMER: [ source: Node(NODE_TYPE: Order), destination: Node(NODE_TYPE: Customer) ], description : ' Order is associated with Customer '}, 

                { ORDER_HAS_PRODUCTS : [ source: Node(NODE_TYPE: Order), destination: Node(NODE_TYPE: Product) ], description : ' Order contains one or more products '}, 
                { PRODUCT_SUPPLIED_BY: [ source: Node(NODE_TYPE: Product), destination: Node(NODE_TYPE: Supplier) ], description : ' Product is supplied by one or more suppliers '}, 
                { SUPPLIER_SUPPLIES_PRODUCT: [ source: Node(NODE_TYPE: Supplier), destination: Node(NODE_TYPE: Product) ], description : ' Product is supplied by one or more suppliers }, 

                { PRODUCT_BELONGS_TO_CATEGORY: [ source: Node(NODE_TYPE: Product), destination: Node(NODE_TYPE: Category) ], description : ' Product belongs to a specific category '},
                { CATEGORY_HAS_PRODUCTS: [ source: Node(NODE_TYPE: Category), destination: Node(NODE_TYPE: Product) ], description : ' Category has one or more product '},
            ]
"""
output_format = "{\"cypher_query\":\"Only Generated cypher query for questions. If multiple relationship exists, make sure to follow 8th RULE.\",\"io_node_information\":\"Every WHERE clause attribute used in query as key and value as JSON\", \"unspecified_data\":\"Data which is ambigous and it's NODE_TYPE can be multiple nodes from schema as python list of string engulfed in double quotes.\",\"output_node\":\"return user's final ask which matches with NODE_TYPE in schema or else  return \"None\".\"}"
query = "What categories does Monica have?"
question = query
cypher_generation_prompt = f"""Relationships and query may not have exact wordings. RULES: \n1. For the generation of open cypher query use node fields NODE_ID and DESCRIPTION in condition of NODE and generate cypher query only using provided relationships and schema.\n2. There can be chances where, to reach final output one need to traverse multiple nodes.\n3.Output can have multiple nodes.\n4. Bidirectional edge Traversal means source node to destination node and destination to source can be traversed. Uni directional edge traversal means only source to destination can be traversed but destination to source cannot be traversed. Please check edge traversal during generating relationships in cypher query\n5. DO NOT write Node Type in Match instead give it in WHERE clause.\n6. In RETURN statement always give appropriate alias for row.\n7. For COUNT and aggregator function always return with attribute of NODE Eg. COUNT(q.NODE_ID).\n8. MOST IMPORTANT RULE: Strictly use one or multiple different relations in MATCH clause as shown if needed. Do NOT combine two relations even though they are continous.\n Eg. \"MATCH (q)-[e1]->(a), (a)-[e2]->(p)\" .\n9.Generated Cypher query should follow given schema and specified relationships only.\n 10. If in query user asks for tasks, return name of tasks. If in query user asks for Qgate, return name of Qgate. If query does not contains any of the node type or relationship type for output node, return \"\".\n11. If user asks question(s) replace it with Qgate.\n12.If exact data is provided in user question generate query. If data provided is ambigous and  node type for given data is not menyioned do not generate the query, only return unspecified_data. unspecified_data should contain explicitly user defined nodes and conditions in list.\n13 Always give relationship value in WHERE clause for every relationship defined in MATCH clause. It should also contain list of data for which user has not provided NODE_TYPE or RELATIONSHIP_TYPE explicitly. Any data which is part of pre defined list of Phase and mentioned in user question, treat it as Phase.Predefined List of phases - [\"Prepare\",\"Deployment(Deploy)\",\"Realize\",\"Run\",\"Execute\"]\n14. Do not generate the cypher query if no valid relationships exists between the nodes in provided schema.\n15.Always analyze the whole schema and use shortest route and minimum relationships to reach output node.\n\nExample of generated Cypher based on user question:\nUser question: \"What are the Realise phase Qgate questions for topic extensibility?\".\n The generated cypher should follow this query syntax : \" MATCH (p)-[e1]->(t), (t)-[e2]->(q) WHERE (p.DESCRIPTION = 'Realize' OR p.NODE_ID = 'Realize') AND p.NODE_TYPE = 'Phase' AND (t.DESCRIPTION = 'extensibility' OR t.NODE_ID = 'extensibility') AND t.NODE_TYPE = 'Topic' AND q.NODE_TYPE = 'Qgate' AND e1.RELATIONSHIP_TYPE = 'HAS_TOPIC_FROM_PHASE' AND e2.RELATIONSHIP_TYPE = 'HAS_QGATE_FROM_TOPIC' RETURN q.DESCRIPTION AS Questions\". \n\nExample for output_node:\nUser Question : \"Get all answers for extensibility\".\n Here output_node is \"Answer\". Check which node user is expecting as output. \n\nExample for unspecified data :\nUser Question : Which products are associated with Michael Brown?.Here, Michael Brown is ambiguous, so it becomes unspecified_data as we don't know whether Michael Brown is Supplier or Customer. output_node is answer. Since Michael Brown is ambiguous, generated cypher is empty and eventually io_node_information is also empty. Output :\"cpyher_query\":\"\"io_node_information\":\"None\", \"unspecified_data\":\"[\"Michael Brown\"]\",\"ouput_node\":\"Answer\"Instructions:\n 1.DO NOT use any other relationship types or properties that are not provided in following schema.\n2.Do not assume NODE_TYPE of any data in question while generating open cypher query following above RULES. If NODE_TYPE is not mentioned in question, STRICTLY identify that data is unspecified_data.\n3.If no unspecified data then follow RULE no 8, STRICTLY.\nSchema: {schema}\n\nThe question is: {question}. \n\n\nOutput Format : {output_format}\nDo not include any explanations or details in your responses. The output shoud be parsable json object which can be passed to json.loads() in python."""
batch_messages = [
            [
                HumanMessage(content="You are an AI assistant which generates open cypher query using the given schema and its relations only if relation_ship exists between them.While generating query you double check it. Generate Open Cypher statement to query a SAP HANA graph workspace."),
                AIMessage(content= "Provide me the RULES and user question."),
                HumanMessage(content=cypher_generation_prompt)
            ]
    ]
resp = chat_model.generate(batch_messages)
resp = json.loads(resp.model_dump_json())
cypher_query_prompt_response = resp['generations'][0][0]["message"]["content"]
embeddings = init_embedding_model('text-embedding-ada-002')
# cursor = self.db.cursor()

response = json.loads(cypher_query_prompt_response)
attributes = {}
is_where_clause_replacement_needed = True
node_sql_query = f"SELECT TOP 1 *, COSINE_SIMILARITY(NODE_VECTOR, TO_REAL_VECTOR(?)) AS SIMILARITY FROM ERP_NODES ORDER BY COSINE_SIMILARITY(NODE_VECTOR, TO_REAL_VECTOR(?)) DESC;"
if type(response["unspecified_data"]) == str:
    response["unspecified_data"] = json.loads(response["unspecified_data"])

#User query has unspecified data.
if len(response["unspecified_data"]) > 0:
    for entry in response["unspecified_data"]:
        entry_CAPS = entry.upper()
        node_id_query = """SELECT TOP 1 * FROM ERP_NODES WHERE NODE_ID = ?"""
        cursor.execute(node_id_query, (entry_CAPS))
        query_res = cursor.fetchall()
        # Check if unspecified data has matching NODE_ID from our system
        if len(query_res) != 0:
            replacement = str(query_res[0][3]) + " " + str(query_res[0][0])
            # Replace unspecified ID with it's nodetype
            query = query.replace(entry, replacement)
        else:
            # Check if unspecified data has matching Description from our system
            entry_vector = str(embeddings.embed_query(entry))
            cursor.execute(node_sql_query, (entry_vector, entry_vector))
            node_sql_query_response = cursor.fetchall()
            if float(node_sql_query_response[0][5]) > 0.88:
                temp = ""
                temp = node_sql_query_response[0][3] + " " + node_sql_query_response[0][2]
                 # Replace unspecified Description with it's nodetype
                query = query.replace(entry, temp)
    new_question = query
    batch_messages = [
            [
                SystemMessage(content="You are an AI assistant which generates open cypher query using the given schema and its relations only if relation_ship exists between them.While generating query you double check it. Generate Open Cypher statement to query a SAP HANA graph workspace."),
                AIMessage(content= "Provide me the RULES and user question."),
                HumanMessage(content=f"""Relationships and query may not have exact wordings. RULES: \n1. For the generation of open cypher query use node fields NODE_ID and DESCRIPTION in condition of NODE and generate cypher query only using provided relationships and schema.\n2. There can be chances where, to reach final output one need to traverse multiple nodes.\n3.Output can have multiple nodes.\n4. Bidirectional edge Traversal means source node to destination node and destination to source can be traversed. Uni directional edge traversal means only source to destination can be traversed but destination to source cannot be traversed. Please check edge traversal during generating relationships in cypher query\n5. DO NOT write Node Type in Match instead give it in WHERE clause.\n6. In RETURN statement always give appropriate alias for row.\n7. For COUNT and aggregator function always return with attribute of NODE Eg. COUNT(q.NODE_ID).\n8. MOST IMPORTANT RULE: Strictly use one or multiple different relations in MATCH clause as shown if needed. Do NOT combine two relations even though they are continous.\n Eg. \"MATCH (q)-[e1]->(a), (a)-[e2]->(p)\" .\n9.Generated Cypher query should follow given schema and specified relationships only.\n 10. If in query user asks for tasks, return name of tasks. If in query user asks for Qgate, return name of Qgate. If query does not contains any of the node type or relationship type for output node, return \"\".\n11. If user asks question(s) replace it with Qgate.\n12.If exact data is provided in user question generate query. If data provided is ambigous and  node type for given data is not menyioned do not generate the query, only return unspecified_data. unspecified_data should contain explicitly user defined nodes and conditions in list.\n13 Always give relationship value in WHERE clause for every relationship defined in MATCH clause. It should also contain list of data for which user has not provided NODE_TYPE or RELATIONSHIP_TYPE explicitly. Any data which is part of pre defined list of Phase and mentioned in user question, treat it as Phase.Predefined List of phases - [\"Prepare\",\"Deployment(Deploy)\",\"Realize\",\"Run\",\"Execute\"]\n14. Do not generate the cypher query if no valid relationships exists between the nodes in provided schema.\n15.Always analyze the whole schema and use shortest route and minimum relationships to reach output node.\n\nExample of generated Cypher based on user question:\nUser question: \"What are the Realise phase Qgate questions for topic extensibility?\".\n The generated cypher should follow this query syntax : \" MATCH (p)-[e1]->(t), (t)-[e2]->(q) WHERE (p.DESCRIPTION = 'Realize' OR p.NODE_ID = 'Realize') AND p.NODE_TYPE = 'Phase' AND (t.DESCRIPTION = 'extensibility' OR t.NODE_ID = 'extensibility') AND t.NODE_TYPE = 'Topic' AND q.NODE_TYPE = 'Qgate' AND e1.RELATIONSHIP_TYPE = 'HAS_TOPIC_FROM_PHASE' AND e2.RELATIONSHIP_TYPE = 'HAS_QGATE_FROM_TOPIC' RETURN q.DESCRIPTION AS Questions\". \n\nExample for output_node:\nUser Question : \"Get all answers for extensibility\".\n Here output_node is \"Answer\". Check which node user is expecting as output. \n\nExample for unspecified data :\nUser Question : Which products are associated with Michael Brown?.Here, Michael Brown is ambiguous, so it becomes unspecified_data as we don't know whether Michael Brown is Supplier or Customer. output_node is answer. Since Michael Brown is ambiguous, generated cypher is empty and eventually io_node_information is also empty. Output :\"cpyher_query\":\"\"io_node_information\":\"None\", \"unspecified_data\":\"[\"Michael Brown\"]\",\"ouput_node\":\"Answer\"Instructions:\n 1.DO NOT use any other relationship types or properties that are not provided in following schema.\nSchema: {schema}\n\nThe question is: {new_question}. \n\n\nOutput Format : {output_format}\nDo not include any explanations or details in your responses. The output shoud be parsable json object which can be passed to json.loads() in python.""")
            ]
    ]
    # Again make the LLM call to generate the cypher query but with more enhanced data.
    resp = chat_model.generate(batch_messages)
    resp = json.loads(resp.model_dump_json())
    response = resp['generations'][0][0]["message"]["content"]

    response = json.loads(response)
    is_where_clause_replacement_needed = False

else:
    # If there is no unspcified data, make sure that whatever present in WHERE clause of generated cypher query has 
    # correct details as it STRING search to database.
    io_node_information = response["io_node_information"]
    if type(io_node_information) == str:
        io_node_information = io_node_information.replace("'",'"')
        io_node_information = json.loads(io_node_information)
    for key, value in io_node_information.items():
        val = value
        if "DESCRIPTION" in key:
            node_sql_query = f"SELECT TOP 1 *, COSINE_SIMILARITY(NODE_VECTOR, TO_REAL_VECTOR(?)) AS SIMILARITY FROM ERP_NODES ORDER BY COSINE_SIMILARITY(NODE_VECTOR, TO_REAL_VECTOR(?)) DESC;"
            value_vector = str(embeddings.embed_query(value))
            cursor.execute(node_sql_query, (value_vector, value_vector))
            attribute_result = cursor.fetchall()
            if float(attribute_result[0][5]) > 0.88:
                val = attribute_result[0][2]
        attributes.update({key: val})
if is_where_clause_replacement_needed:
    final_cypher_query = replace_where_clause(response["cypher_query"], attributes)
else:
    final_cypher_query = response["cypher_query"]
output_node = response["output_node"]


#Making a Graph Workspace query and retrieving the answer.
if final_cypher_query == '':
    print("Query not generated")
else:
    final_cypher_query = final_cypher_query.replace("'", "''")
    final_sql_query = f"""SELECT * FROM OPENCYPHER_TABLE( GRAPH WORKSPACE "DBADMIN"."ERP" QUERY ' {final_cypher_query} ');"""
    cursor.execute(final_sql_query)
    sql_query_response = cursor.fetchall()
    if len(sql_query_response) == 0:
        print("No data found")
    else:
        db_data = ""
        for row in sql_query_response:
            db_data = db_data + "-"
            db_data = db_data + str(row[0])
            db_data = db_data + "\n"

        final_response = db_data
        print(final_response)
