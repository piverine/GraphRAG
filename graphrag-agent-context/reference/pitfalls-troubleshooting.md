# Common Pitfalls & Troubleshooting Guide

| Pitfall | Why It Happens | Mitigation |
|---|---|---|
| Sparse, disconnected graph | Ingested papers are topically unrelated | Curate a focused, single-subfield corpus (Phase 1) |
| Duplicate entities (GPT-4 vs GPT4) | No entity resolution step | Normalize on insert + Cypher `MERGE` (Phase 3) |
| Cypher generation fails or traverses the wrong direction | LLM lacks examples of this specific schema's conventions | Few-shot examples + retry-on-error (Phase 5) |
| Extraction misses relationships spanning sentence boundaries | Chunking cuts across a relationship-describing sentence | Increase chunk overlap; consider paragraph-aware splitting (Phase 2) |
| Answers aren't actually grounded | Synthesis prompt doesn't constrain the LLM to retrieved facts | Explicit grounding prompt (Phase 7) |
| Upload requests time out | Ingestion is slow and run synchronously | Dispatch as a background task (Phase 8) |
| Schema too rigid, missing real relationships | Initial schema didn't anticipate a common relationship type in the corpus | Review extraction output early; extend schema deliberately and document why |
| Frontend graph visualization is unreadable at scale | Force-directed layouts get cluttered beyond ~50-100 nodes | Filter/limit the subgraph returned per query to what's relevant to the question |

When debugging, isolate the failure to a single phase before making changes — most failures trace back to Phase 3 (extraction quality) even when they visibly manifest in Phase 5 or 6 (retrieval/query results). Check the Neo4j browser first.
