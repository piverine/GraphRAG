# Phase 7: Answer Synthesis & Grounding

## Goal
Turn a retrieved subgraph into a written answer that is explicitly constrained to those facts — this is what preserves the project's core verifiability claim.

## Grounded Synthesis Prompt
```python
SYNTHESIS_PROMPT = """
You are answering a question using ONLY the graph facts provided below.
Do not use any outside knowledge. If the facts do not contain enough
information to answer, say so explicitly rather than guessing.

For each claim in your answer, reference which fact(s) support it.

Graph facts:
{retrieved_subgraph}

Question: {question}
"""
```

## Why This Is Required
Without this explicit constraint, the final LLM call is free to blend retrieved facts with training-data knowledge — silently reintroducing the hallucination risk the entire graph-retrieval pipeline exists to eliminate. This is not optional polish; it's the mechanism that makes the "grounded, verifiable answers" claim true rather than aspirational.

## Citing Sources
Because provenance metadata (Phase 4) links every node/relationship back to its source chunk/paper, the synthesis step should attach a citation to each claim, e.g.: "BERT improves on Word2Vec [source: Devlin et al., 2018]."

## Definition of Done
- [ ] Synthesis prompt explicitly restricts the model to provided graph facts
- [ ] Tested against a question where the graph has insufficient information — confirm the model says so rather than fabricating an answer
- [ ] Citations/source references appear in synthesized answers where provenance data is available
