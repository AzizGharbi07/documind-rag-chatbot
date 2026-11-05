# DocuMind

> **Kurzfassung (DE):** DocuMind ist ein lokal laufender RAG-Chatbot: Dokumente (PDF, DOCX, TXT, Markdown) hochladen, Fragen stellen, Antworten **nur aus den Dokumenten** mit Quellenangaben erhalten. Läuft komplett lokal mit Ollama, ohne GPU.

A local-first retrieval-augmented chatbot for your documents. Answers come **only** from the uploaded files, with citations (file, page, snippet); if the documents don't contain the answer, it says so.

> 🚧 Work in progress. Milestone 1 (skeleton, Docker Compose, CI) is done. See [Roadmap](#roadmap).

## Quick start

**Requirements:** Docker Desktop, [Ollama](https://ollama.com) on the host, about 8 GB free RAM, about 4 GB disk for models. No GPU needed.

```bash
cp .env.example .env
ollama pull qwen2.5:3b
ollama pull bge-m3
docker compose up --build
```

Open http://localhost:3000. The header shows whether Postgres, Qdrant and Ollama are reachable.
API docs: http://localhost:8000/api/docs.

No host Ollama? Run it in Docker instead: set `DOCKER_OLLAMA_BASE_URL=http://ollama:11434` in `.env`, then `docker compose --profile ollama up --build` and pull the models with `docker compose exec ollama ollama pull bge-m3` (and the same for `qwen2.5:3b`).

## Development

With [`just`](https://github.com/casey/just) (`winget install Casey.Just`):

| Command | What it does |
|---|---|
| `just setup` | install backend + frontend deps, git hooks |
| `just infra` | start only Postgres + Qdrant in Docker |
| `just dev-api` / `just dev-web` | backend (reload) / frontend (HMR) on the host |
| `just check` | everything CI runs: lint, format, types, tests |

## Architecture

See [docs/architecture.md](docs/architecture.md) and the decision records in [docs/decisions/](docs/decisions/).

## Tech stack

| Area | Choice |
|---|---|
| Backend | Python 3.12, FastAPI, Pydantic v2, SQLAlchemy 2 (async) + Alembic, uv |
| LLM / embeddings | Ollama (`qwen2.5:3b`, `bge-m3`), behind a swappable interface |
| Storage | PostgreSQL (metadata, source of truth), Qdrant (vectors) |
| Frontend | React 19, TypeScript, Vite, Tailwind CSS, TanStack Query |
| Quality | pytest, Ruff, mypy (strict), oxlint, Prettier, Vitest, pre-commit |
| Infra / CI | Docker Compose, GitHub Actions, Dependabot |

## Evaluation

_Coming in milestone 6._

## Design decisions and trade-offs

_Summarised at the end; details in [docs/decisions/](docs/decisions/)._

## Limitations

_To be written._

## Roadmap

- [x] M1 Repo skeleton, Docker Compose, CI
- [ ] M2 Ingestion pipeline
- [ ] M3 Retrieval + chat API (+ retrieval mini-eval)
- [ ] M4 Frontend chat with streaming
- [ ] M5 Citations + "I don't know" behaviour
- [ ] M6 Evaluation harness
- [ ] M7 Hybrid search + reranker
- [ ] M8 Polish, demo GIF
