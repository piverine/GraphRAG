# Project Overview

## What This Is

A full-stack GraphRAG (Graph-based Retrieval-Augmented Generation) application that maps academic literature. It ingests research papers (PDFs), uses an LLM (Gemini 2.5 Flash) to extract entities and relationships into a knowledge graph (Neo4j), and answers complex, multi-hop questions by traversing that graph — producing answers that are traceable back to specific source papers, rather than generated purely from the model's internal knowledge.

## Problem Statement

Standard RAG (vector similarity search over document chunks) can answer simple lookup questions ("what dataset did this paper use?") but cannot answer questions that require chaining multiple relationships together, such as:

- "How has attention mechanism research evolved?" (requires tracing a multi-step lineage)
- "Which papers contradict each other on transformer efficiency claims?" (requires an explicit contradiction relationship, not just topical similarity)
- "What areas of this field are under-researched?" (requires analyzing graph connectivity/sparsity, which has no equivalent in flat text search)

Vector similarity search finds text that *sounds* related to a query. It has no mechanism for representing or traversing typed, directional relationships between entities. A knowledge graph does.

## Core Capabilities to Build

1. **Algorithm lineage tracing** — multi-hop traversal of `IMPROVES` relationships (e.g., Transformer → Attention → downstream optimizations).
2. **Contradiction finding** — direct queries against `CONTRADICTS` relationships to surface opposing studies.
3. **Literature gap analysis** — identifying nodes with sparse or zero connectivity as a proxy for under-explored areas.

## Target User

PhD candidates, academic researchers, and R&D engineers who need to process large volumes of unstructured literature and require verifiable, non-hallucinated answers backed by explicit, inspectable relationships — not just plausible-sounding generated text.

## Non-Negotiable Design Principles

- **Grounding over fluency.** Every synthesized answer must be traceable to specific extracted facts. If the graph doesn't contain enough information to answer, the system must say so rather than fill the gap from the model's general knowledge.
- **Schema discipline.** Node and relationship types are fixed and constrained (see `docs/01-architecture.md`). The extraction step must not be allowed to invent arbitrary categories — this is what keeps the graph queryable and consistent.
- **No local GPU dependency.** All LLM computation is offloaded to the Gemini API. The local machine only runs Neo4j, FastAPI, and Next.js.

## What "Done" Looks Like

A working system where a user can:
1. Upload a PDF and see it processed into graph nodes/edges within a reasonable time.
2. Ask a free-form question in a chat interface and receive a grounded answer.
3. See the subgraph of facts that produced that answer, visually, alongside the text answer.
4. Run each of the three headline queries (lineage, contradiction, gap analysis) and get non-trivial results against a real, multi-paper corpus.
