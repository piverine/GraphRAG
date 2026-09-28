import os
import shutil
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from ingestion.parser import parse_and_chunk_pdf
from ingestion.extractor import ingest_paper_to_neo4j
from ingestion.database import get_graph_summary, get_neo4j_graph
from retrieval.cypher_chain import query_knowledge_graph
from retrieval.headline_queries import (
    get_algorithm_lineage,
    get_contradictions,
    get_literature_gaps
)

app = FastAPI(
    title="GraphRAG Academic Literature Mapping API",
    description="FastAPI backend for GraphRAG ingesting research papers into Neo4j and answering grounded questions.",
    version="1.0.0"
)

# Enable CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

PAPERS_DIR = os.path.join(os.path.dirname(__file__), "papers")
os.makedirs(PAPERS_DIR, exist_ok=True)

class QueryRequest(BaseModel):
    question: str

def process_ingestion_background(filepath: str):
    """Background task function to process paper chunks into Neo4j."""
    try:
        print(f"Starting background ingestion for: {filepath}")
        chunks = parse_and_chunk_pdf(filepath)
        ingest_paper_to_neo4j(chunks)
        print(f"Successfully finished background ingestion for: {filepath}")
    except Exception as e:
        print(f"Error during background ingestion of {filepath}: {e}")

@app.get("/health")
def health_check():
    """Liveness check and Neo4j database status."""
    try:
        summary = get_graph_summary()
        return {
            "status": "healthy",
            "neo4j_connected": True,
            "database_stats": summary
        }
    except Exception as e:
        return {
            "status": "degraded",
            "neo4j_connected": False,
            "error": str(e)
        }

@app.get("/graph/summary")
def graph_summary():
    """Returns node and relationship counts."""
    return get_graph_summary()

@app.post("/upload")
async def upload_pdf(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    """Accepts a research paper PDF and dispatches background ingestion."""
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
        
    file_path = os.path.join(PAPERS_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Run ingestion as background task to prevent request timeout
    background_tasks.add_task(process_ingestion_background, file_path)
    
    return {
        "status": "processing",
        "message": f"Paper '{file.filename}' uploaded successfully. Ingestion queued in background.",
        "filename": file.filename
    }

@app.post("/query")
def query_graph(payload: QueryRequest):
    """Executes Text-to-Cypher query and returns grounded answer with intermediate subgraph steps."""
    if not payload.question.strip():
        raise HTTPException(status_code=400, detail="Question must not be empty.")
        
    result = query_knowledge_graph(payload.question)
    result["subgraph"] = result.get("intermediate_steps", [])
    return result

@app.get("/headline/lineage")
def headline_lineage(alg_id: str = "Attention"):
    """Returns multi-hop algorithm lineage chain."""
    return {"algorithm": alg_id, "lineage": get_algorithm_lineage(alg_id)}

@app.get("/headline/contradictions")
def headline_contradictions():
    """Returns contradictory research statements in corpus."""
    return {"contradictions": get_contradictions()}

@app.get("/headline/gaps")
def headline_gaps():
    """Returns literature gaps (concepts ranked by low connection degree)."""
    return {"gaps": get_literature_gaps()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
