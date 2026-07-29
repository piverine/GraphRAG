import os
import re
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
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key or api_key == "your_gemini_api_key_here":
        raise ValueError(
            "GOOGLE_API_KEY environment variable is missing or default. "
            "Please set a valid Gemini API key in your .env file."
        )
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
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
        # Remove trailing periods
        cleaned = cleaned.rstrip(".")
        # Standardize common variations
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

def extract_graph_from_chunks(chunks: List[Document]) -> List[GraphDocument]:
    """Extracts entities and relationships from chunks using Gemini 2.5 Flash."""
    llm = get_llm()
    transformer = LLMGraphTransformer(
        llm=llm,
        allowed_nodes=ALLOWED_NODES,
        allowed_relationships=ALLOWED_RELATIONSHIPS,
        node_properties=["description"],
    )
    
    graph_docs = transformer.convert_to_graph_documents(chunks)
    normalized_docs = normalize_graph_documents(graph_docs)
    return normalized_docs

def ingest_paper_to_neo4j(chunks: List[Document]):
    """Extracts graph documents and saves them to Neo4j with source provenance."""
    graph_docs = extract_graph_from_chunks(chunks)
    graph = get_neo4j_graph(refresh_schema=False)
    
    # Store with include_source=True to bind metadata provenance
    graph.add_graph_documents(
        graph_docs,
        baseEntityLabel=True,
        include_source=True
    )
    return len(graph_docs)
