# 0003. oxlint instead of ESLint, just instead of make

- Status: accepted
- Date: 2026-11-04

## Context
The brief asked for ESLint and a Makefile or justfile. The current Vite React template ships oxlint and TypeScript 7 (the native compiler). `make` is not installed on Windows by default.

## Decision
- Keep **oxlint** (with the React and TypeScript plugins) plus Prettier. It implements the commonly used ESLint rules, runs in milliseconds, and works with TypeScript 7 without extra setup. Type checking itself is done by `tsc`.
- Use a **justfile**. `just` installs with one `winget` command and behaves the same on Windows and Linux. Everything also works with plain `docker compose`, `uv` and `npm` commands, so `just` is optional.

## Consequences
- Fewer lint rules than a full typescript-eslint setup with type-aware rules. If that becomes a gap, adding ESLint for those rules alone is a small change.
