# ADR 001: DuckDB as the local analytical store

- **Status:** Accepted
- **Date:** 2026-11-05

## Context
The agent needs to run aggregations (sum, group by, top-N, period comparisons) over a few hundred thousand to a few million contract actions. The answers must be reproducible and must not depend on live API latency. The project also has to run on a laptop, in a single Docker container, and on a free Streamlit or Hugging Face host with no managed database.

## Options considered
| Option | Pros | Cons |
|---|---|---|
| **Query the USASpending API live for every question** | Always fresh, no storage | 2 to 10s per call, rate limits, no ad-hoc group-bys, results drift between eval runs |
| **SQLite** | Ubiquitous, single file | Row-oriented and slow for analytical scans, weak `DECIMAL` support |
| **Postgres** | Production-grade | Needs a server, so it doesn't fit free hosting or a one-command demo |
| **DuckDB** | Columnar, fast aggregations, single file, `DECIMAL`, reads Parquet/JSON natively, embeds in Python | Single writer, not a multi-user OLTP store |

## Decision
Use **DuckDB** in a single file (`data/fedlens.duckdb`). The batch pipeline is the only writer. The app and the evals open it read-only.

## Consequences
- Evals run against a fixed snapshot, so scores are comparable across prompt and model changes.
- Ground truth for evals is a direct SQL query over the same file, separate from the agent's code path.
- `refresh_data` (optional tool) has to take the write lock briefly. It is disabled in the hosted demo.
- **Migration path:** the schema is plain SQL with natural keys, so it ports to Delta tables on Databricks (see the `databricks-port` branch) or to Postgres without redesign.
