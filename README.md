# Jira Mail Assistant

LLM + RAG prototype for automatically qualifying incoming client requests.

Analyzes a client email, extracts the key information, retrieves the relevant PowerCARD documentation, and pre-fills a Jira ticket, reviewed and approved by a human before creation.

## How it works

**Offline** — the PowerCARD documentation is parsed, chunked, embedded, and indexed in Qdrant along with its metadata (document type, module, version).

**Online** — for each email:

1. The email enters the system (paste or `.eml` upload)
2. An LLM extracts the key fields and generates a structured summary
3. RAG retrieval identifies the most relevant documents
4. The reviewer validates and corrects the result through the UI
5. The Jira ticket is created with its fields pre-filled

No ticket is written to Jira without explicit human approval.

## Architecture

![Architecture overview](documentation/assets/simple_archi.jpg)

*Draft architecture, subject to change.*

## Stack

| Component | Choice |
| --- | --- |
| API | FastAPI + Pydantic |
| LLM | Azure OpenAI or local Mistral (swappable) |
| Embeddings | `multilingual-e5-large` |
| Vector store | Qdrant |
| Queue + state | PostgreSQL |
| UI | Streamlit |
| Infra | Docker Compose |

## Structure

```text
schemas/     # Pydantic models - the shared end-to-end contract
services/    # pure business logic (extraction, retrieval, Jira mapping)
clients/     # swappable wrappers (LLM, embeddings, Qdrant, Jira)
api/         # FastAPI routes
worker/      # job processing loop
ingestion/   # offline documentation pipeline
db/          # Postgres models and queries
ui/          # Streamlit review interface
```

## Getting started

```bash
cp .env.example .env     # configure LLM_PROVIDER, JIRA_*, QDRANT_*
docker compose up
```

- API: http://localhost:8000 (docs: `/docs`)
- Review UI: http://localhost:8501

Index the documentation:

```bash
docker compose run --rm worker python -m ingestion.run --path ./docs
```