# Common commands. Install just: `winget install Casey.Just`. Run `just` to list recipes.
# Recipes run in PowerShell on Windows and sh elsewhere, so they stay single-line and portable.
set windows-shell := ["powershell.exe", "-NoLogo", "-NoProfile", "-Command"]
set dotenv-load := true

default:
    @just --list

# One-time setup: install backend + frontend deps and the git hooks
setup:
    cd backend; uv sync
    cd frontend; npm ci
    cd backend; uv run pre-commit install

# Download the configured models into host Ollama
pull-models:
    ollama pull {{env("LLM_MODEL", "qwen2.5:3b")}}
    ollama pull {{env("EMBEDDING_MODEL", "bge-m3")}}

# Full stack in Docker (http://localhost:3000)
up:
    docker compose up --build -d

down:
    docker compose down

logs service="":
    docker compose logs -f {{service}}

# Only Postgres + Qdrant in Docker, for running api/frontend on the host
infra:
    docker compose up -d postgres qdrant

# Backend with auto-reload on the host (needs `just infra`)
dev-api:
    cd backend; uv run alembic upgrade head; uv run uvicorn app.main:app --reload

# Frontend dev server with HMR (http://localhost:5173)
dev-web:
    cd frontend; npm run dev

# Create a migration from model changes: just migration "add documents table"
migration message:
    cd backend; uv run alembic revision --autogenerate -m "{{message}}"

lint:
    cd backend; uv run ruff check .; uv run ruff format --check .; uv run mypy app tests
    cd frontend; npm run lint; npm run format:check; npm run typecheck

fmt:
    cd backend; uv run ruff check --fix .; uv run ruff format .
    cd frontend; npm run format

test:
    cd backend; uv run pytest
    cd frontend; npm test

# Everything CI runs
check: lint test
