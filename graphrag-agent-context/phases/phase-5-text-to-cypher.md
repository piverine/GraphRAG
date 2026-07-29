# Phase 5: Natural Language to Cypher (Text-to-Cypher)

## Goal
Translate free-form user questions into Cypher queries reliably. This is the most fragile part of the system — build in mitigations from the start, not as an afterthought.

## Baseline Implementation
```python
from langchain_neo4j import GraphCypherQAChain

chain = GraphCypherQAChain.from_llm(
    llm=llm,
    graph=graph,
    verbose=True,
    allow_dangerous_requests=True,  # required acknowledgment flag
)

response = chain.invoke({"query": "Which algorithms improve on Word2Vec?"})
```
Internally this runs two LLM calls: (1) the LLM is shown the graph schema (`graph.schema`) and writes Cypher to answer the question, (2) the raw Cypher results are passed to a second LLM call that writes a natural-language answer.

## Known Failure Modes
- **Syntax errors** — malformed Cypher that Neo4j rejects.
- **Wrong relationship direction** — `(A)-[:IMPROVES]->(B)` is not the same as `(B)-[:IMPROVES]->(A)`; a reversed pattern returns an empty (not erroring) result, which is worse because it fails silently.
- **Schema drift** — if the LLM isn't given an accurate current schema view, it may reference labels/types that don't exist.

## Mitigation 1: Few-Shot Examples (highest leverage improvement)
```python
examples = [
  {
    "question": "What did BERT improve on?",
    "cypher": "MATCH (a:Algorithm {id: 'BERT'})-[:IMPROVES]->(b) RETURN b"
  },
  {
    "question": "Which papers contradict each other about GPT-3?",
    "cypher": "MATCH (a)-[:CONTRADICTS]-(b) WHERE a.id = 'GPT-3' OR b.id = 'GPT-3' RETURN a, b"
  },
]
```
Provide these examples specific to this schema, inserted into the prompt before the user's question. This shows the model the exact direction conventions of this schema rather than relying on inference from a bare schema description.

## Mitigation 2: Retry-on-Error
```python
def run_cypher_with_retry(question, max_attempts=2):
    for attempt in range(max_attempts):
        try:
            return chain.invoke({"query": question})
        except Exception as e:
            if attempt == max_attempts - 1:
                raise
            question = f"{question}\n(Previous attempt failed with: {e}. Please correct the Cypher.)"
```

## Definition of Done
- [ ] `GraphCypherQAChain` runs successfully against the ingested graph
- [ ] At least 5 hand-written few-shot examples specific to this schema are included in the prompt
- [ ] Retry-on-error is implemented and tested against at least one deliberately malformed question
- [ ] 5+ free-form test questions return correct or reasonably correct Cypher, verified manually
