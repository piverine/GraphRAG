# Phase 0: Environment Setup

## Goal
A fully working local environment, verified layer by layer, before any application code is written.

## Prerequisites
- Docker Desktop or Docker Engine (Linux)
- Python 3.10+
- Node.js 18+ and npm
- A Google AI Studio API key for Gemini 2.5 Flash

## Steps

### 1. Run Neo4j
```bash
docker run \
  --name neo4j-graphrag \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  -d neo4j:latest
```
- Port `7474`: Neo4j browser UI at `http://localhost:7474` — use constantly during development to visually inspect the graph.
- Port `7687`: Bolt protocol — the binary channel application code uses to query the database.

**Verify:** open `http://localhost:7474`, log in with `neo4j` / `password`, run `RETURN 1`. Confirm it returns before proceeding.

### 2. Python environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install fastapi uvicorn langchain langchain-neo4j \
    langchain-google-genai langchain-experimental \
    pypdf python-multipart arxiv --break-system-packages
```

### 3. Environment variables
Create `.env`:
```
GOOGLE_API_KEY=your_gemini_api_key_here
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=password
```

### 4. Next.js project
```bash
npx create-next-app@latest graphrag-frontend --tailwind --app
cd graphrag-frontend
npm install react-force-graph-2d axios
```

## Definition of Done
- [ ] `docker ps` shows the Neo4j container running
- [ ] Neo4j browser UI loads at `localhost:7474` and accepts login
- [ ] `RETURN 1` executes successfully in the Neo4j browser
- [ ] Python venv activates and all packages import without error
- [ ] `.env` file exists and is not committed to version control (add to `.gitignore`)
- [ ] Next.js dev server starts with `npm run dev` and loads a default page

Do not proceed to Phase 1 until every box above is checked — debugging environment issues alongside application logic is significantly harder than isolating them here.
