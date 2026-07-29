# System Architecture

## High-Level Component Diagram

```mermaid
flowchart TB
    subgraph Frontend["Next.js Frontend"]
        UP[Upload Page]
        CH[Chat Page]
        GV[Graph Visualizer]
    end

    subgraph Backend["FastAPI Backend"]
        EP1["/upload endpoint"]
        EP2["/query endpoint"]
        ING[Ingestion Pipeline]
        RET[Retrieval Pipeline]
    end

    subgraph LLM["Gemini 2.5 Flash (via API)"]
        EX[Entity/Relation Extraction]
        CY[Text-to-Cypher]
        SY[Answer Synthesis]
    end

    DB[(Neo4j Graph DB)]

    UP -->|POST PDF| EP1
    CH -->|POST question| EP2
    EP1 --> ING
    EP2 --> RET
    ING --> EX
    EX --> DB
    RET --> CY
    CY --> DB
    DB --> SY
    SY --> RET
    RET --> CH
    RET --> GV
```

## Ingestion Pipeline (Sequence)

```mermaid
sequenceDiagram
    participant U as User
    participant FE as Next.js
    participant API as FastAPI
    participant LLM as Gemini
    participant DB as Neo4j

    U->>FE: Upload PDF
    FE->>API: POST /upload
    API->>API: Parse PDF, chunk text
    loop each chunk
        API->>LLM: Extract entities/relationships (schema-constrained)
        LLM-->>API: Structured triplets
    end
    API->>DB: MERGE nodes and relationships (with provenance)
    API-->>FE: Extraction summary (N entities, M relationships)
```

## Query Pipeline (Sequence)

```mermaid
sequenceDiagram
    participant U as User
    participant FE as Next.js
    participant API as FastAPI
    participant LLM as Gemini
    participant DB as Neo4j

    U->>FE: Ask question
    FE->>API: POST /query
    API->>LLM: Translate question to Cypher (schema + few-shot examples)
    LLM-->>API: Cypher query
    API->>DB: Execute Cypher
    DB-->>API: Subgraph (nodes + relationships)
    API->>LLM: Synthesize grounded answer from subgraph only
    LLM-->>API: Answer + citations
    API-->>FE: {answer, subgraph}
    FE->>U: Show answer + rendered subgraph
```

## Data Model

```mermaid
erDiagram
    Researcher ||--o{ Algorithm : DEVELOPED
    Algorithm ||--o{ Algorithm : IMPROVES
    Algorithm ||--o{ Dataset : EVALUATED_ON
    Algorithm ||--o{ Algorithm : CONTRADICTS
    Concept }o--o{ Algorithm : "related (implicit via extraction)"
```

**Node types (fixed schema):** `Researcher`, `Algorithm`, `Dataset`, `Metric`, `Concept`

**Relationship types (fixed schema):** `DEVELOPED`, `EVALUATED_ON`, `IMPROVES`, `CONTRADICTS`

> Do not add node/relationship types outside this list without explicit instruction. If extraction consistently misses a real relationship in the source text because the schema doesn't cover it, flag this rather than silently expanding the schema.

## Component Responsibilities

| Component | Responsibility |
|---|---|
| Next.js frontend | PDF upload UI, chat UI, graph visualization of retrieved subgraphs |
| FastAPI backend | Orchestrates ingestion and query pipelines; exposes `/upload` and `/query` |
| LangChain (extraction) | Wraps Gemini calls for structured triplet extraction from text chunks |
| LangChain (retrieval) | Wraps Gemini calls for text-to-Cypher generation and answer synthesis |
| Neo4j | Stores the knowledge graph; executes Cypher traversal queries |
| Gemini 2.5 Flash | Performs all extraction, query translation, and generation reasoning |

## Why This Stack (for when the agent needs to justify a choice)

- **Neo4j over a relational DB or in-memory graph library:** native graph storage makes multi-hop traversal a constant-time operation regardless of database size, versus deeply nested joins in a relational schema. This directly serves the lineage-tracing feature.
- **LangChain over hand-rolled prompt code:** standardizes extraction (`LLMGraphTransformer`) and retrieval (`GraphCypherQAChain`) patterns instead of reimplementing prompt templates and response parsers from scratch. It is a thin orchestration layer — it is not doing anything conceptually novel, just saving reimplementation.
- **Gemini 2.5 Flash:** large context window reduces the need for extremely aggressive chunking, lowering the risk of splitting a described relationship across two chunks.
- **FastAPI:** native async support matters because both pipelines are I/O-bound (LLM calls, DB queries); automatic validation from type hints reduces boilerplate.
- **Docker for Neo4j:** isolates the database from host configuration, makes resets trivial during development, mirrors real deployment patterns.
