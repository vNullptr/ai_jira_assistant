# Jira Issue Assistant

On-demand assistant for Jira Service Management support threads powered by LLM and RAG architecture.

A support engineer invokes the assistant on a request. It reads the full thread, produces a structured summary of the request and its current state, finds the most relevant documentation, and posts both back as an internal comment.

## Why

Support handles most client requests directly in the thread. Creating tickets is not the bottleneck. What still costs time is picking up a long thread to understand where it stands, and hunting through specifications, change requests, technical guides, and API documentation to find the relevant reference.

## How it works

**Offline** — the documentation corpus is parsed, chunked, embedded, and indexed in Qdrant with its metadata (document type, module, version).

**Online** — per invocation:

1. A support engineer invokes the assistant on a request
2. A Jira webhook triggers processing
3. The full comment thread is fetched via the Jira API
4. An LLM extracts the key fields and summarizes the thread's current state
5. RAG retrieval identifies the most relevant documents
6. The result is posted as an **internal** comment: summary plus documents with links

Nothing is ever visible to the client. The assistant posts internal comments only, and the support engineer decides what to use.

## Design principles

- **On demand, not continuous.** Every invocation is an explicit signal that help is needed. No processing of threads that do not need it.
- **Internal only.** Suggestions are for the team, never for the client.

## Architecture

![Architecture Diagram](documentation/assets/architecture.jpg)

## Stack

| Component | Choice |
| --- | --- |
| API | FastAPI + Pydantic |
| LLM | Azure OpenAI or local Mistral (swappable) |
| Embeddings | HF embedding model `multilingual-e5-large` |
| Vector store | Qdrant (swappable) |
| Queue + state | PostgreSQL |
| Trigger | Jira webhook |
| Fallback UI | Streamlit |
| Observability | Langfuse |
| Infra | Docker Compose |

## Structure

```text
schema/        # Pydantic models - the shared end-to-end contract
services/      # pure business logic (extraction, summarization, retrieval)
clients/       # swappable wrappers (LLM, embeddings, Qdrant, Jira)
api/           # FastAPI routes, webhook handler
worker/        # job processing loop
ingestion/     # offline documentation pipeline
db/            # Postgres models and queries
documentation/ # Contains all of the project generated documentation
```

## Getting started

For local webhook development, expose the API with a tunnel (ngrok, Cloudflare Tunnel) and register the public URL in Jira.