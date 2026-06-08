# Deployment Guide

This service can be deployed anywhere that supports Docker plus PostgreSQL with pgvector.

## Required Services

- Web service running this repository's `Dockerfile`
- PostgreSQL database with the `vector` extension enabled
- OpenAI API key

## Environment Variables

```env
OPENAI_API_KEY=your-real-key
DATABASE_URL=postgresql://user:password@host:5432/database
OPENAI_CHAT_MODEL=gpt-4o-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
RETRIEVAL_LIMIT=5
```

## Database Setup

Run the SQL in `migrations/001_init.sql` once against the production database.

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

The migration creates the `document_chunks` table and cosine similarity index.

## Render Deployment

1. Push this project to GitHub.
2. Create a PostgreSQL database that supports pgvector.
3. Create a new Render Web Service from the repository.
4. Use Docker as the runtime.
5. Add the environment variables above.
6. Run `migrations/001_init.sql` against the database.
7. Deploy and verify `https://your-service.onrender.com/docs`.

## Smoke Test

After deployment, open `/docs`, ingest a document with `POST /documents`, then ask a question with `POST /ask`.

