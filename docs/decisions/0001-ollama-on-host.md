# 0001. Run Ollama on the host by default

- Status: accepted
- Date: 2026-11-04

## Context
The target machine is a Windows 11 laptop with 16 GB RAM and no GPU. Inside Docker Desktop, Ollama runs in the WSL2 VM, which adds memory overhead and makes GPU use (where available) awkward. A native install is faster and keeps models outside Docker volumes.

## Decision
The `api` container reaches host Ollama at `http://host.docker.internal:11434` (configurable via `DOCKER_OLLAMA_BASE_URL`). An `ollama` service in a Compose profile covers machines without a host install.

## Consequences
- Quick start has one extra step (install Ollama and pull models).
- Model downloads (~3 GB) happen once, outside `docker compose up`.
- `/api/health/ready` reports a missing Ollama or missing models clearly instead of failing at the first chat request.
