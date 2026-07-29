# Phase 8: Backend API Design (FastAPI)

## Goal
Expose the ingestion and query pipelines as HTTP endpoints the frontend can call.

## Routes
| Route | Method | Purpose |
|---|---|---|
| `/upload` | POST | Accept a PDF, run ingestion pipeline, return extraction summary |
| `/query` | POST | Accept a question, run retrieval pipeline, return answer + subgraph |
| `/graph/summary` | GET | Return current node/relationship counts |
| `/health` | GET | Basic liveness check for Neo4j connectivity |

## Upload Endpoint
```python
from fastapi import FastAPI, UploadFile, BackgroundTasks

app = FastAPI()

@app.post("/upload")
async def upload_pdf(file: UploadFile, background_tasks: BackgroundTasks):
    path = f"./papers/{file.filename}"
    with open(path, "wb") as f:
        f.write(await file.read())

    background_tasks.add_task(ingest_paper, path)
    return {"status": "processing", "filename": file.filename}
```
Ingestion runs as a **background task**, not inline — extraction over a full paper can take tens of seconds to a couple of minutes, and holding an HTTP request open that long risks a client timeout. `BackgroundTasks` is a reasonable, correctly-scoped choice for this project's size; a production system would use a proper job queue (Celery/RQ) with a polling endpoint.

## Query Endpoint
```python
@app.post("/query")
async def query_graph(payload: QueryRequest):
    cypher_result = run_cypher_with_retry(payload.question)
    answer = synthesize_answer(cypher_result, payload.question)
    return {
        "answer": answer,
        "subgraph": cypher_result["intermediate_steps"],
    }
```
Return the raw subgraph alongside the answer, not just text — this is what enables the frontend graph visualizer (Phase 9) and is itself part of the verifiability story.

## Definition of Done
- [ ] `/upload` accepts a PDF, dispatches ingestion as a background task, returns immediately
- [ ] `/query` returns both a synthesized answer and the raw subgraph used to produce it
- [ ] `/health` confirms Neo4j connectivity
- [ ] Basic request validation is in place (file type check on upload, non-empty question on query)
