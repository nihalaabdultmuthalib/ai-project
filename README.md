# AI QA Service

Small AI-powered REST API built with FastAPI, OpenAI, PostgreSQL, and pgvector.

## Features

- `POST /documents` chunks text and stores OpenAI embeddings in PostgreSQL.
- `GET /documents` lists recent stored chunks for demos and debugging.
- `POST /ask` embeds the question, retrieves similar chunks with pgvector cosine search, and asks the LLM to answer from retrieved context.
- `GET /health` checks database connectivity.
- Docker Compose starts both the API and PostgreSQL with pgvector.
- Mocked tests cover the API without making real OpenAI calls.

## Local Setup

1. Create an environment file:

```powershell
Copy-Item .env.example .env
```

2. Add your real `OPENAI_API_KEY` to `.env`.

3. Start the full stack:

```powershell
docker compose up --build
```

4. Open the API docs:

```text
http://localhost:8000/docs
```

If you run only the FastAPI app without Docker:

```powershell
uvicorn main:app --reload --port 8002
```

Then open:

```text
http://127.0.0.1:8002/docs
```

## Example Requests

Ingest a document:

```powershell
Invoke-RestMethod -Method Post http://localhost:8000/documents `
  -ContentType "application/json" `
  -Body '{"source":"assessment.txt","content":"This project is a FastAPI AI QA service using PostgreSQL pgvector retrieval and OpenAI."}'
```

Ask a question:

```powershell
Invoke-RestMethod -Method Post http://localhost:8000/ask `
  -ContentType "application/json" `
  -Body '{"question":"What database does this service use for retrieval?"}'
```

List documents:

```powershell
Invoke-RestMethod http://localhost:8000/documents
```

Seed demo data after `.env` and PostgreSQL are ready:

```powershell
python scripts/seed.py
```

## Architecture

```text
Client -> FastAPI -> OpenAI embeddings -> PostgreSQL pgvector search
                 -> OpenAI chat completion -> Answer + sources
```

PostgreSQL stores document chunks in `document_chunks`. The `embedding` column uses `vector(1536)`, matching `text-embedding-3-small`, and an IVFFlat cosine index improves nearest-neighbor search.

## Deployment Notes

Recommended simple deployment:

- API: Render, Railway, Fly.io, AWS App Runner, Azure Container Apps, or Google Cloud Run.
- Database: managed PostgreSQL with the `vector` extension enabled.
- Required environment variables:
  - `OPENAI_API_KEY`
  - `DATABASE_URL`
  - `OPENAI_CHAT_MODEL`
  - `OPENAI_EMBEDDING_MODEL`
  - `RETRIEVAL_LIMIT`

For Render or Railway, deploy from this repository, set the Dockerfile as the build target, attach a PostgreSQL database, enable pgvector, run `migrations/001_init.sql`, and set the environment variables above. See `DEPLOYMENT.md` for a step-by-step deployment guide. A `render.yaml` starter config is included.

## Development Without Docker

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload
```

You still need a PostgreSQL database with pgvector and the schema from `migrations/001_init.sql`.

## Testing

```powershell
pytest
```
