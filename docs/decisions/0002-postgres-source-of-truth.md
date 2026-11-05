# 0002. PostgreSQL is the source of truth, Qdrant a derived index

- Status: accepted
- Date: 2026-11-04

## Context
Documents live in two stores: metadata and chunk text in PostgreSQL, vectors in Qdrant. There is no transaction across both, so a crash between writes can leave them out of sync.

## Decision
PostgreSQL owns documents and chunks and tracks a status per document (`pending → processing → ready | failed`). Every Qdrant point carries `doc_id` and `chunk_id` in its payload. Deleting or re-indexing removes points by `doc_id` filter, and that operation is idempotent.

## Consequences
- The vector index can be dropped and rebuilt from PostgreSQL, e.g. when changing the embedding model.
- Only documents in `ready` state are searchable, so half-ingested documents never appear in answers.
- Slight duplication: chunk text is stored in both places (Qdrant payload for fast retrieval).
