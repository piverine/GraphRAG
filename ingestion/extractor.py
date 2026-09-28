import os
import re
import time
from typing import List
from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_community.graphs.graph_document import GraphDocument, Node, Relationship
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_google_genai import ChatGoogleGenerativeAI
from ingestion.database import get_neo4j_graph

load_dotenv()

# Fixed constrained schema
ALLOWED_NODES = ["Researcher", "Algorithm", "Dataset", "Metric", "Concept"]
ALLOWED_RELATIONSHIPS = ["DEVELOPED", "EVALUATED_ON", "IMPROVES", "CONTRADICTS"]

def get_llm():
    groq_api_key = os.getenv("GROQ_API_KEY")
    if groq_api_key and groq_api_key != "your_groq_api_key_here":
        from langchain_groq import ChatGroq
        model = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
        return ChatGroq(
            model=model,
            temperature=0,
            groq_api_key=groq_api_key
        )
        
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key or api_key == "your_gemini_api_key_here":
        raise ValueError(
            "Neither GROQ_API_KEY nor GOOGLE_API_KEY is configured in your .env file."
        )
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash-lite",
        temperature=0,
        google_api_key=api_key
    )

def normalize_entity_id(entity_id: str, label: str) -> str:
    """
    Applies entity resolution rules to avoid duplicate nodes
    (e.g., 'BERT', 'bert', 'GPT-3', 'GPT 3' -> clean canonical representations).
    """
    if not entity_id:
        return entity_id
    
    cleaned = entity_id.strip()
    
    if label == "Algorithm":
        # Keep standard acronyms uppercase, e.g., BERT, GPT-3, RoBERTa
        cleaned = cleaned.rstrip(".")
        if re.match(r"^gpt[\s\-]?3$", cleaned, re.IGNORECASE):
            return "GPT-3"
        if re.match(r"^gpt[\s\-]?4$", cleaned, re.IGNORECASE):
            return "GPT-4"
        if re.match(r"^bert$", cleaned, re.IGNORECASE):
            return "BERT"
        if re.match(r"^roberta$", cleaned, re.IGNORECASE):
            return "RoBERTa"
        if re.match(r"^xlnet$", cleaned, re.IGNORECASE):
            return "XLNet"
        if re.match(r"^transformer$", cleaned, re.IGNORECASE):
            return "Transformer"
        if re.match(r"^flashattention$", cleaned, re.IGNORECASE):
            return "FlashAttention"
            
    return cleaned

def normalize_graph_documents(graph_docs: List[GraphDocument]) -> List[GraphDocument]:
    """
    Mutates/normalizes extracted node IDs and relationship references
    for entity resolution across papers.
    """
    for doc in graph_docs:
        id_mapping = {}
        
        # Normalize nodes
        for node in doc.nodes:
            original_id = str(node.id)
            norm_id = normalize_entity_id(original_id, node.type)
            id_mapping[original_id] = norm_id
            node.id = norm_id

        # Update relationships to point to normalized node IDs
        for rel in doc.relationships:
            orig_source = str(rel.source.id)
            orig_target = str(rel.target.id)
            
            rel.source.id = id_mapping.get(orig_source, orig_source)
            rel.target.id = id_mapping.get(orig_target, orig_target)
            
    return graph_docs

def extract_graph_from_chunks(chunks: List[Document], rate_limit_delay: float = 5.5) -> List[GraphDocument]:
    """
    Extracts entities and relationships from chunks using Gemini with
    rate-limiting delay and exponential backoff retry for HTTP 429 quota errors.
    """
    llm = get_llm()
    transformer = LLMGraphTransformer(
        llm=llm,
        allowed_nodes=ALLOWED_NODES,
        allowed_relationships=ALLOWED_RELATIONSHIPS,
        node_properties=["description"],
    )
    
    all_graph_docs = []
    total_chunks = len(chunks)
    
    for idx, chunk in enumerate(chunks):
        max_retries = 5
        success = False
        
        for attempt in range(max_retries):
            try:
                single_docs = transformer.convert_to_graph_documents([chunk])
                all_graph_docs.extend(single_docs)
                success = True
                break
            except Exception as e:
                err_str = str(e)
                if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str or "Quota exceeded" in err_str:
                    wait_time = 30.0 + (attempt * 15)
                    print(f"  ⚠️ [Rate Limit 429] Quota exceeded on chunk {idx+1}/{total_chunks}. Pausing {wait_time}s before retry (attempt {attempt+1}/{max_retries})...")
                    time.sleep(wait_time)
                else:
                    print(f"  ⚠️ [Error] Unhandled error on chunk {idx+1}/{total_chunks}: {e}")
                    break
        
        # Polite delay between chunks to respect API RPM limit (15 requests/min)
        if success and rate_limit_delay > 0 and idx < total_chunks - 1:
            time.sleep(rate_limit_delay)
            
    normalized_docs = normalize_graph_documents(all_graph_docs)
    return normalized_docs

def save_graph_documents_to_neo4j(graph_docs: List[GraphDocument]) -> int:
    """Directly persists GraphDocuments to Neo4j via MERGE without requiring APOC procedures."""
    if not graph_docs:
        return 0
    graph = get_neo4j_graph(refresh_schema=False)
    total_nodes = 0
    
    for gd in graph_docs:
        paper_id = gd.source.metadata.get("paper_id") or gd.source.metadata.get("source_file") or "unknown"
        graph.query("MERGE (d:Document {id: $doc_id})", params={"doc_id": paper_id})
        
        for n in gd.nodes:
            label = n.type if n.type in ALLOWED_NODES else "Concept"
            graph.query(
                f"MERGE (n:{label} {{id: $id}}) MERGE (d:Document {{id: $doc_id}}) MERGE (n)-[:MENTIONED_IN]->(d)",
                params={"id": str(n.id), "doc_id": paper_id}
            )
            total_nodes += 1
            
        for r in gd.relationships:
            s_label = r.source.type if r.source.type in ALLOWED_NODES else "Concept"
            t_label = r.target.type if r.target.type in ALLOWED_NODES else "Concept"
            rel_type = r.type if r.type in ALLOWED_RELATIONSHIPS else "IMPROVES"
            graph.query(
                f"""
                MATCH (s:{s_label} {{id: $s_id}})
                MATCH (t:{t_label} {{id: $t_id}})
                MERGE (s)-[:{rel_type}]->(t)
                """,
                params={"s_id": str(r.source.id), "t_id": str(r.target.id)}
            )
            
    return total_nodes

def ingest_paper_to_neo4j(chunks: List[Document]):
    """Extracts graph documents and saves them to Neo4j with source provenance."""
    if not chunks:
        return 0
    graph_docs = extract_graph_from_chunks(chunks)
    nodes_saved = save_graph_documents_to_neo4j(graph_docs)
    return nodes_saved
