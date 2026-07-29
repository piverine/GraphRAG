import os
import sys
from typing import Dict, Any, List

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from ingestion.database import get_neo4j_graph

def get_algorithm_lineage(algorithm_id: str = "Attention") -> List[Dict[str, Any]]:
    """
    Headline Feature 1: Algorithm Lineage Tracing (multi-hop)
    Traverses IMPROVES relationships transitively (1 to 5 hops).
    """
    graph = get_neo4j_graph(refresh_schema=False)
    cypher = """
    MATCH path = (start:Algorithm)<-[:IMPROVES*1..5]-(descendant:Algorithm)
    WHERE toLower(start.id) = toLower($alg_id)
    RETURN [n in nodes(path) | n.id] AS lineage_chain,
           length(path) AS hops
    ORDER BY hops ASC
    """
    try:
        results = graph.query(cypher, {"alg_id": algorithm_id})
        return results
    except Exception as e:
        print(f"Error executing lineage query: {e}")
        return []

def get_contradictions() -> List[Dict[str, Any]]:
    """
    Headline Feature 2: Contradiction Discovery
    Queries CONTRADICTS relationships symmetrically and fetches source papers.
    """
    graph = get_neo4j_graph(refresh_schema=False)
    cypher = """
    MATCH (a)-[:CONTRADICTS]-(b)
    OPTIONAL MATCH (a)-[:MENTIONED_IN]->(doc_a:Document)
    OPTIONAL MATCH (b)-[:MENTIONED_IN]->(doc_b:Document)
    RETURN DISTINCT a.id AS entity_a, 
                    b.id AS entity_b, 
                    doc_a.id AS paper_a, 
                    doc_b.id AS paper_b
    """
    try:
        results = graph.query(cypher)
        return results
    except Exception as e:
        print(f"Error executing contradiction query: {e}")
        return []

def get_literature_gaps() -> List[Dict[str, Any]]:
    """
    Headline Feature 3: Literature Gap Analysis
    Identifies Concept nodes with low node degree (sparse/zero connections).
    """
    graph = get_neo4j_graph(refresh_schema=False)
    cypher = """
    MATCH (n:Concept)
    OPTIONAL MATCH (n)-[r]-()
    WITH n, count(r) AS degree
    RETURN n.id AS concept, degree
    ORDER BY degree ASC
    LIMIT 20
    """
    try:
        results = graph.query(cypher)
        return results
    except Exception as e:
        print(f"Error executing literature gap query: {e}")
        return []

if __name__ == "__main__":
    print("Testing headline query procedures...")
    print("Lineage (Attention):", get_algorithm_lineage("Attention"))
    print("Contradictions:", get_contradictions())
    print("Literature Gaps:", get_literature_gaps())
