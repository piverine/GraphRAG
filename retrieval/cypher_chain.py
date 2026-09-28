import os
import sys
from typing import Dict, Any, List
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_neo4j import GraphCypherQAChain
from langchain_core.prompts import PromptTemplate

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from ingestion.database import get_neo4j_graph

load_dotenv()

# Few-shot Cypher generation prompt tailored to fixed schema
CYPHER_GENERATION_TEMPLATE = """
Task: Generate Cypher statement to query a Neo4j graph database for academic research questions.
Instructions:
Use only the provided relationship types and node labels in the schema.
Do not use any other relationship types or labels that are not mentioned.

Node Labels:
- Researcher (id)
- Algorithm (id, description)
- Dataset (id)
- Metric (id)
- Concept (id)

Relationship Types:
- DEVELOPED: (Researcher)-[:DEVELOPED]->(Algorithm)
- EVALUATED_ON: (Algorithm)-[:EVALUATED_ON]->(Dataset)
- IMPROVES: (Algorithm)-[:IMPROVES]->(Algorithm)
- CONTRADICTS: (Algorithm/Researcher/Concept)-[:CONTRADICTS]-(Algorithm/Researcher/Concept)

Examples:
Question: Which algorithms improve on BERT?
Cypher: MATCH (a:Algorithm)-[:IMPROVES]->(b:Algorithm {{id: 'BERT'}}) RETURN a.id AS Algorithm

Question: What algorithms did Vaswani develop?
Cypher: MATCH (r:Researcher)-[:DEVELOPED]->(a:Algorithm) WHERE toLower(r.id) CONTAINS 'vaswani' RETURN a.id AS Algorithm

Question: What datasets was FlashAttention evaluated on?
Cypher: MATCH (a:Algorithm {{id: 'FlashAttention'}})-[:EVALUATED_ON]->(d:Dataset) RETURN d.id AS Dataset

Question: Which studies or algorithms contradict each other?
Cypher: MATCH (a)-[:CONTRADICTS]-(b) RETURN a.id AS EntityA, b.id AS EntityB

Schema:
{schema}

Question: {question}
Cypher:"""

CYPHER_PROMPT = PromptTemplate(
    input_variables=["schema", "question"],
    template=CYPHER_GENERATION_TEMPLATE
)

SYNTHESIS_TEMPLATE = """
You are an academic literature assistant answering a user question based on the retrieved graph database facts below.
Do not use outside knowledge.
If the graph facts do not contain the answer, state: "The ingested knowledge graph does not contain sufficient information to answer this question."

Graph facts:
{context}

Question: {question}
Answer directly and concisely:
"""

SYNTHESIS_PROMPT = PromptTemplate(
    input_variables=["context", "question"],
    template=SYNTHESIS_TEMPLATE
)

def get_cypher_qa_chain():
    groq_api_key = os.getenv("GROQ_API_KEY")
    if groq_api_key and groq_api_key != "your_groq_api_key_here":
        from langchain_groq import ChatGroq
        model = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
        llm = ChatGroq(
            model=model,
            temperature=0,
            groq_api_key=groq_api_key
        )
    else:
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key or api_key == "your_gemini_api_key_here":
            raise ValueError("Neither GROQ_API_KEY nor GOOGLE_API_KEY is configured in your .env file.")
            
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash-lite",
            temperature=0,
            google_api_key=api_key
        )
    
    graph = get_neo4j_graph(refresh_schema=False)
    
    chain = GraphCypherQAChain.from_llm(
        llm=llm,
        graph=graph,
        cypher_prompt=CYPHER_PROMPT,
        qa_prompt=SYNTHESIS_PROMPT,
        verbose=True,
        allow_dangerous_requests=True,
        return_intermediate_steps=True
    )
    return chain

def query_knowledge_graph(question: str, max_attempts: int = 2) -> Dict[str, Any]:
    """Queries the graph with retry logic for Cypher syntax issues."""
    chain = get_cypher_qa_chain()
    current_question = question
    
    for attempt in range(max_attempts):
        try:
            res = chain.invoke({"query": current_question})
            return {
                "question": question,
                "answer": res.get("result", ""),
                "intermediate_steps": res.get("intermediate_steps", [])
            }
        except Exception as e:
            print(f"Cypher QA attempt {attempt + 1} failed: {e}")
            if attempt == max_attempts - 1:
                return {
                    "question": question,
                    "answer": f"Unable to execute graph query: {str(e)}",
                    "intermediate_steps": []
                }
            if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e) or "rate" in str(e).lower():
                import time
                time.sleep(5)
            current_question = f"{question}\n(Note: previous query failed with: {e}. Generate valid Cypher.)"
