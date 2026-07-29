# GraphRAG for Academic Literature Mapping — Agent Context Index

This folder is structured context for an AI coding agent building this project. Read files in the order below. Each phase file is self-contained and includes goals, working code, and a "done when" checklist so the agent can verify completion before moving to the next phase.

## Read Order

1. `docs/00-overview.md` — what this project is and why, in one pass
2. `docs/03-communication-protocol.md` — **read this second, not last.** It governs how you interact with the user throughout the entire build, starting from your very first message, not just once code-writing begins.
3. `docs/01-architecture.md` — system architecture and diagrams (read before writing any code)
4. `docs/02-glossary.md` — terminology reference (consult as needed, not required up front)
5. `phases/phase-0-environment-setup.md`
6. `phases/phase-1-data-acquisition.md`
7. `phases/phase-2-parsing-chunking.md`
8. `phases/phase-3-extraction.md`
9. `phases/phase-4-graph-storage.md`
10. `phases/phase-5-text-to-cypher.md`
11. `phases/phase-6-headline-features.md`
12. `phases/phase-7-synthesis-grounding.md`
13. `phases/phase-8-backend-api.md`
14. `phases/phase-9-frontend.md`
15. `reference/testing-evaluation.md` — consult during and after each phase
16. `reference/pitfalls-troubleshooting.md` — consult when something breaks
17. `reference/security-production.md` — apply before considering any phase "production-ready"
18. `reference/cost-performance.md` — consult when estimating API usage
19. `reference/extensions.md` — optional, only after core build is complete
20. `reference/checklist.md` — master checklist across all phases

## Build Rules for the Agent

- **Keep the user informed at every step.** Follow `docs/03-communication-protocol.md` exactly — explain what you're about to do before doing it, what happened after you do it, and what you're fixing and why whenever something breaks. This applies for the entire build, not just at phase boundaries. The user wants to understand the system as it's built, not receive it as a finished black box.
- **Do not skip phases.** Each phase depends on the previous one producing working, verified output — not just code that compiles.
- **Verify before advancing.** Each phase file ends with a "Definition of Done" section. Do not proceed to the next phase until those conditions are met.
- **Prefer the schema and conventions given in these files exactly as specified**, unless the user explicitly asks for a deviation. The node/relationship schema in particular must stay consistent across all phases — changing it midway breaks previously ingested data.
- **When a code sample is given, treat it as a working reference implementation**, not pseudocode — it is written to run as-is against the stack specified in `docs/01-architecture.md`, with only file paths/credentials needing adjustment.
- **Ask before deviating** from the stack specified (Next.js, FastAPI, Neo4j, LangChain, Gemini 2.5 Flash) — these choices are deliberate and justified in `docs/01-architecture.md`.

## Tech Stack Summary

| Layer | Technology |
|---|---|
| Frontend | Next.js + Tailwind CSS |
| Backend | FastAPI (Python) |
| Database | Neo4j (Docker) |
| LLM | Google Gemini 2.5 Flash |
| Orchestration | LangChain, langchain-neo4j, langchain-google-genai, langchain-experimental |
| Environment | Linux, no local GPU required |
