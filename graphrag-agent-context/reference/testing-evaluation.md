# Testing, Evaluation & Quality Metrics

## Extraction Quality
After ingesting each paper, manually inspect resulting nodes/relationships in the Neo4j browser against your own reading of the paper. This manual review loop is the primary debugging tool during Phase 3.

## Retrieval Quality
Build a small hand-written test set of (question, expected answer characteristics) pairs before it's needed for a demo — checkable properties, not exact strings ("the answer should mention RoBERTa and BERT," "the answer should say no contradictions were found for X"). Re-run this set after any change to schema, chunking, or the Cypher generation prompt to catch regressions.

## Evaluation Table Template
| Question | Expected in answer | Pass/Fail |
|---|---|---|
| What improves on Word2Vec? | BERT, GloVe (or whatever the corpus contains) | — |
| What is the lineage from Attention to its descendants? | Multi-hop chain, at least 2 generations | — |
| Which papers contradict each other on benchmark X? | At least one named pair, or explicit "none found" | — |
| What concepts are under-connected in the graph? | A plausible, non-empty list | — |

## Fallback Strategy for Live Demos
If text-to-Cypher fails unpredictably during a live demo, having 3-4 pre-verified example questions mapped to hand-checked Cypher is a legitimate safety net, not a workaround to be ashamed of — production RAG systems commonly ship an "example questions" UI for exactly this reason. Prepare this list in advance.
