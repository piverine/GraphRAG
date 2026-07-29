# Phase 4: Graph Data Modeling & Storage

## Goal
Persist extracted graph documents into Neo4j with provenance, indexes, and constraints.

## Pushing Data into Neo4j
```python
from langchain_neo4j import Neo4jGraph

graph = Neo4jGraph(
    url="bolt://localhost:7687",
    username="neo4j",
    password="password",
)

graph.add_graph_documents(
    graph_documents,
    baseEntityLabel=True,
    include_source=True,
)
```
`include_source=True` links each extracted fact back to its source document chunk — this is what makes provenance (and therefore citation in final answers) possible.

## Indexes and Constraints
```cypher
CREATE CONSTRAINT unique_algorithm_id IF NOT EXISTS
FOR (a:Algorithm) REQUIRE a.id IS UNIQUE;

CREATE INDEX researcher_name_index IF NOT EXISTS
FOR (r:Researcher) ON (r.id);
```
Add a uniqueness constraint per node label to enforce entity resolution at the database level, not just in application code.

## Visual Inspection
After every ingestion batch, run in the Neo4j browser:
```cypher
MATCH (n) RETURN n LIMIT 100
```
This is the fastest way to catch extraction problems — malformed nodes, missing relationships, unexpectedly sparse graphs — before they compound into confusing downstream query bugs.

## Definition of Done
- [ ] All extracted graph documents from Phase 3 are pushed into Neo4j
- [ ] Uniqueness constraints exist for each node label
- [ ] `MATCH (n) RETURN n LIMIT 100` shows a visibly connected graph, not isolated fragments
- [ ] Spot-check a few nodes for correct provenance links back to source documents
