# Phase 3: Entity & Relationship Extraction

## Goal
Extract schema-constrained triplets from each text chunk using Gemini via LangChain's `LLMGraphTransformer`. This phase determines the quality of everything downstream — treat it as deserving the most testing and manual review time in the whole project.

## Fixed Schema (do not deviate without explicit instruction)
- **Node types:** `Researcher`, `Algorithm`, `Dataset`, `Metric`, `Concept`
- **Relationship types:** `DEVELOPED`, `EVALUATED_ON`, `IMPROVES`, `CONTRADICTS`

This schema directly supports the three headline features: lineage via `IMPROVES`, contradictions via `CONTRADICTS`, gap analysis via sparse connectivity across any node type.

## Implementation
```python
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)

graph_transformer = LLMGraphTransformer(
    llm=llm,
    allowed_nodes=["Researcher", "Algorithm", "Dataset", "Metric", "Concept"],
    allowed_relationships=["DEVELOPED", "EVALUATED_ON", "IMPROVES", "CONTRADICTS"],
    node_properties=["description"],
)

graph_documents = graph_transformer.convert_to_graph_documents(chunks)
```
`temperature=0` is required — extraction is a parsing task, not a creative one; deterministic, literal output is what you want.

## What's Happening Under the Hood
LangChain constructs a prompt instructing Gemini to read the chunk and return a structured list of nodes/relationships strictly from the allowed lists (typically JSON-like), then parses that into `Node`/`Relationship` Python objects wrapped in a `GraphDocument`. This is prompt engineering plus a parser — not a fundamentally different kind of model. Be able to explain it this way rather than treating it as a black box.

## Entity Resolution (required, not optional)
Raw extraction produces duplicates for the same real-world entity across papers ("GPT-4," "GPT4," "gpt-4"). Unresolved, this silently breaks multi-hop queries.

1. **Normalize on insert** — lowercase, strip punctuation/whitespace, before writing any node.
2. **Use Cypher's `MERGE`** instead of `CREATE` — inserts a node only if an equivalent one (matched by a property) doesn't already exist.
3. **(Optional, advanced)** fuzzy-match near-duplicates via embedding similarity above a threshold, flagged for merge.

## Definition of Done
- [ ] Extraction runs on one test paper; output manually inspected in the Neo4j browser and checked against your own reading of the paper for missed/incorrect entities
- [ ] Entity normalization is applied before any node insertion
- [ ] `MERGE` (not `CREATE`) is used for node insertion
- [ ] Full corpus extraction completes without unhandled errors
