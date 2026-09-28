import os
import sys
import argparse
from typing import Set

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from ingestion.parser import parse_and_chunk_pdf
from ingestion.extractor import ingest_paper_to_neo4j
from ingestion.database import get_neo4j_graph, get_graph_summary

PAPERS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "papers")

def get_ingested_paper_ids() -> Set[str]:
    """Returns set of paper_ids already present in Neo4j."""
    try:
        graph = get_neo4j_graph(refresh_schema=False)
        res = graph.query("MATCH (d:Document) RETURN d.id AS doc_id")
        if res:
            return {row["doc_id"] for row in res if row.get("doc_id")}
    except Exception as e:
        print(f"Notice checking existing documents: {e}")
    return set()

def ingest_corpus(limit_papers: int = None, target_paper: str = None, max_chunks: int = None):
    """
    Ingests PDF papers from ./papers directory into Neo4j with rate limiting,
    retry handling, and resume capability.
    """
    if not os.path.exists(PAPERS_DIR):
        print(f"Error: Papers directory '{PAPERS_DIR}' does not exist.")
        return

    pdf_files = sorted([f for f in os.listdir(PAPERS_DIR) if f.endswith(".pdf")])
    if target_paper:
        pdf_files = [f for f in pdf_files if target_paper in f]

    ingested_ids = get_ingested_paper_ids()
    print(f"Found {len(pdf_files)} PDF papers in total.")
    print(f"Already ingested in Neo4j: {len(ingested_ids)} papers ({ingested_ids})")

    pending_files = []
    for f in pdf_files:
        paper_id = f.replace(".pdf", "")
        if paper_id not in ingested_ids:
            pending_files.append(f)

    print(f"Pending papers to ingest: {len(pending_files)}")
    if not pending_files:
        print("✅ All papers in corpus are already ingested into Neo4j!")
        summary = get_graph_summary()
        print(f"Graph Summary: {summary}")
        return

    if limit_papers:
        pending_files = pending_files[:limit_papers]
        print(f"Limiting this run to {limit_papers} paper(s).")

    for idx, filename in enumerate(pending_files, 1):
        filepath = os.path.join(PAPERS_DIR, filename)
        paper_id = filename.replace(".pdf", "")
        print(f"\n==================================================")
        print(f"[{idx}/{len(pending_files)}] Ingesting Paper: {filename} (ID: {paper_id})")
        print(f"==================================================")

        try:
            chunks = parse_and_chunk_pdf(filepath)
            print(f"  📄 Parsed into {len(chunks)} text chunks.")
            if max_chunks and len(chunks) > max_chunks:
                chunks = chunks[:max_chunks]
                print(f"  ⚡ Fast-mode: limited to first {max_chunks} chunks (core paper sections).")
            
            num_docs = ingest_paper_to_neo4j(chunks)
            print(f"  ✅ Successfully extracted and persisted {num_docs} graph documents for {filename}.")
            
            stats = get_graph_summary()
            print(f"  📊 Current DB Status: {stats['node_count']} nodes, {stats['relationship_count']} relationships.")
        except Exception as e:
            print(f"  ❌ Error processing {filename}: {e}")

    final_stats = get_graph_summary()
    print(f"\n🎉 Ingestion batch finished! Final Graph Status: {final_stats}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest research paper corpus into Neo4j.")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of papers to ingest in this run.")
    parser.add_argument("--paper", type=str, default=None, help="Specific paper ID or filename to ingest.")
    parser.add_argument("--max-chunks", type=int, default=None, help="Limit chunks per paper for faster ingestion (e.g. 15).")
    args = parser.parse_args()

    ingest_corpus(limit_papers=args.limit, target_paper=args.paper, max_chunks=args.max_chunks)
