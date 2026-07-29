# Extension Ideas & Future Work

Only pursue these after the core 9-phase build is complete and verified.

## Hybrid Vector + Graph Retrieval
Add a vector index over chunk text alongside the graph. Use vector search to find an entry point into the graph for vague/loosely-worded questions, then traverse from there.

## Temporal Reasoning
Attach publication dates to source documents; expose "how did X evolve over time" as an explicitly time-ordered lineage query.

## Automated Schema Suggestion
Periodically prompt the LLM to review chunks that produced low-confidence or unmatched extractions, and suggest schema extensions — a semi-automated way to evolve the schema rather than only doing so manually.

## Citation-Graph Integration
Combine extracted semantic relationships (`IMPROVES`, `CONTRADICTS`) with papers' actual formal citation graph (via the Semantic Scholar API) to cross-validate: does the citation graph structurally support the semantic relationship the LLM extracted?

## Multi-Agent Extraction Review
Add a second LLM pass that critiques the first extraction pass's output against source text before insertion — a lightweight self-consistency check to catch wrong extractions before they pollute the graph.
