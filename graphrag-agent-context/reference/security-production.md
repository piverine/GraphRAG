# Security & Production Considerations

## Cypher Injection
Because Cypher queries are LLM-generated from user input, there's a structural analog to SQL injection: a maliciously crafted question could attempt to manipulate the LLM into generating a destructive query (`DELETE`, `DETACH DELETE`).

- Run the query-handling database connection with **read-only permissions**, separate from the write-permission connection used only during ingestion.
- **Validate generated Cypher** before execution — reject any query containing write clauses (`CREATE`, `DELETE`, `SET`, `MERGE`) when handling a read-only user question.

## API Key Handling
Never expose the Gemini API key to the frontend. All LLM calls must be proxied through FastAPI, with the key stored server-side as an environment variable, never committed to version control.

## File Upload Validation
Validate uploaded files are genuinely PDFs (not just trusting the extension), enforce a reasonable file size limit, and sanitize filenames before writing to disk to avoid path traversal issues.

## Rate Limiting
Both ingestion and query endpoints call a paid, rate-limited external API (Gemini). Add basic request throttling on your own endpoints to avoid a single user or frontend bug exhausting API quota/budget.
