# Glossary of Terms

Reference for concepts used throughout this project. Consult as needed; not required reading before starting.

| Term | Definition |
|---|---|
| Knowledge graph | A database of facts represented as nodes (entities) and typed, directional edges (relationships), rather than rows/tables or free text. |
| Node | A single entity in the graph — here, a Researcher, Algorithm, Dataset, Metric, or Concept. |
| Edge / Relationship | A typed, directional link between two nodes, e.g. `DEVELOPED`, `IMPROVES`, `EVALUATED_ON`, `CONTRADICTS`. |
| Triplet | The atomic fact unit of a knowledge graph: `(subject) -[relationship]-> (object)`. |
| Schema | The fixed set of allowed node and relationship types, used to constrain extraction and keep the graph consistent. |
| Cypher | Neo4j's graph query language; pattern-matches paths through a graph, syntactically resembling ASCII-art of the pattern being searched. |
| Embedding | A numerical vector representation of text capturing semantic meaning, used for similarity search. |
| Vector database | A database optimized for storing embeddings and retrieving the most similar vectors to a query vector. |
| Chunking | Splitting a long document into smaller text spans before processing, to stay within model context limits and improve extraction accuracy. |
| Named Entity Recognition (NER) | Identifying and classifying named "things" (people, organizations, algorithms) in raw text. |
| Relation extraction | Identifying how two extracted entities relate to each other. |
| LLMGraphTransformer | LangChain utility that prompts an LLM to convert raw text into graph-ready nodes/relationships, conforming to a given schema. |
| GraphDocument | LangChain's intermediate object representing extracted nodes/relationships before insertion into a graph database. |
| Text-to-Cypher | Using an LLM to translate a natural-language question into a Cypher query. |
| GraphCypherQAChain | LangChain chain that automates text-to-Cypher generation, execution, and answer synthesis. |
| Multi-hop reasoning | Answering a question requiring traversal of more than one relationship/edge. |
| Variable-length path | Cypher pattern (`*1..5`) matching chains of a range of lengths — used for lineage/ancestry queries. |
| Entity resolution | Recognizing that differently-written mentions (e.g. "GPT-4" vs "GPT4") refer to the same entity, and merging them. |
| Provenance | Metadata linking an extracted fact back to its source document/chunk, enabling traceability. |
| Grounding | Constraining an LLM's generated answer to only use retrieved, verifiable facts rather than unconstrained internal knowledge. |
| Hallucination | An LLM generating a plausible-sounding but false or unsupported claim. |
| Temperature | Generation parameter controlling randomness; `0` gives deterministic, literal output — preferred for extraction. |
| Few-shot prompting | Including worked examples in a prompt to improve accuracy on a structured task. |
| Bolt protocol | Neo4j's binary network protocol for client queries (default port 7687). |
| Docker container | Isolated, portable runtime environment; used here to run Neo4j without a local install. |
