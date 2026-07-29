# Cost, Performance & Scalability

## Where Cost Comes From
Every extraction chunk, every text-to-Cypher translation, and every answer synthesis is a paid Gemini API call. For a corpus of 20 papers split into ~15-20 chunks each, expect roughly 300-400 extraction calls for ingestion alone. Estimate this against Gemini's published per-token pricing before running the full corpus.

## Reducing Cost During Development
- Cache extraction results locally so restarting the backend doesn't re-extract the same papers.
- Test extraction and Cypher-generation prompt changes against a small 2-3 paper subset before running the full corpus.
- Consider a cheaper/faster Gemini variant for early prompt-iteration cycles, switching to the full Pro model only for final corpus ingestion.

## Scalability
Neo4j scales comfortably into the millions of nodes for a single-instance deployment — well beyond this project's corpus size. The bottleneck in this system is LLM API calls (cost and latency), not the graph database. If asked "would this scale?", the correct answer: the graph storage layer is not the constraint; the extraction/generation pipeline's throughput against a paid, rate-limited API is.
