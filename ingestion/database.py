import os
from dotenv import load_dotenv
from langchain_neo4j import Neo4jGraph

load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

def get_neo4j_graph(refresh_schema: bool = False) -> Neo4jGraph:
    """Returns an authenticated Neo4jGraph instance."""
    return Neo4jGraph(
        url=NEO4J_URI,
        username=NEO4J_USERNAME,
        password=NEO4J_PASSWORD,
        refresh_schema=refresh_schema
    )

def setup_constraints_and_indexes():
    """Sets up database uniqueness constraints and indexes for node labels."""
    graph = get_neo4j_graph(refresh_schema=False)
    node_labels = ["Researcher", "Algorithm", "Dataset", "Metric", "Concept", "Document"]
    
    for label in node_labels:
        constraint_query = f"""
        CREATE CONSTRAINT unique_{label.lower()}_id IF NOT EXISTS
        FOR (n:{label}) REQUIRE n.id IS UNIQUE;
        """
        try:
            graph.query(constraint_query)
        except Exception as e:
            print(f"Notice on constraint for {label}: {e}")

    print("✅ Neo4j database constraints and indexes created.")

def get_graph_summary():
    """Returns node and relationship counts from Neo4j."""
    graph = get_neo4j_graph(refresh_schema=False)
    nodes_res = graph.query("MATCH (n) RETURN count(n) AS node_count")
    rel_res = graph.query("MATCH ()-[r]->() RETURN count(r) AS rel_count")
    labels_res = graph.query("CALL db.labels() YIELD label RETURN label")
    
    node_count = nodes_res[0]["node_count"] if nodes_res else 0
    rel_count = rel_res[0]["rel_count"] if rel_res else 0
    labels = [row["label"] for row in labels_res] if labels_res else []
    
    return {
        "node_count": node_count,
        "relationship_count": rel_count,
        "node_labels": labels
    }

if __name__ == "__main__":
    setup_constraints_and_indexes()
    summary = get_graph_summary()
    print("Graph Summary:", summary)
