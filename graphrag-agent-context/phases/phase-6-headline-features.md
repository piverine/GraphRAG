# Phase 6: The Three Headline Capabilities

## Goal
Hand-write and verify Cypher for each of the three demo-critical features. Do not rely solely on auto-generated Cypher for these — they are the queries most likely to be run live in a demo or interview.

## 1. Algorithm Lineage Tracing (multi-hop)
```cypher
MATCH path = (start:Algorithm {id: "Attention"})<-[:IMPROVES*1..5]-(descendant:Algorithm)
RETURN path
```
`*1..5` is Cypher's variable-length path syntax — matches chains of `IMPROVES` from 1 to 5 hops, returning direct improvements plus improvements-on-improvements transitively, in a single traversal. This is the clearest demonstration of why a graph database beats vector search for this project.

## 2. Contradiction Finding
```cypher
MATCH (a)-[:CONTRADICTS]-(b)
RETURN a, b
```
Note the undirected pattern (`-[:CONTRADICTS]-`, no arrowhead) — a contradiction is symmetric, so match in both directions.

### Refinement: return source papers
```cypher
MATCH (a)-[:CONTRADICTS]-(b)
OPTIONAL MATCH (a)-[:MENTIONED_IN]->(doc_a:Document)
OPTIONAL MATCH (b)-[:MENTIONED_IN]->(doc_b:Document)
RETURN a.id, b.id, doc_a.source, doc_b.source
```

## 3. Literature Gap Analysis
```cypher
MATCH (n:Concept)
WHERE NOT (n)--()
RETURN n
```
Finds Concept nodes with zero connections — a proxy for under-explored ideas in the corpus.

### Sharper version: rank by degree
```cypher
MATCH (n:Concept)
OPTIONAL MATCH (n)-[r]-()
WITH n, count(r) AS degree
RETURN n.id, degree
ORDER BY degree ASC
LIMIT 20
```

## Definition of Done
- [ ] All three queries run successfully against the ingested corpus and return non-trivial, non-empty results
- [ ] Lineage query demonstrates at least a 2-hop chain on the actual ingested data
- [ ] Contradiction query returns at least one real pair from the corpus, or is confirmed to correctly return none if the corpus genuinely has no contradictions
- [ ] Each query is wrapped in a backend function callable from the `/query` endpoint (see `phase-8-backend-api.md`)
