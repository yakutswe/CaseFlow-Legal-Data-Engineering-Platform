# CaseFlow — Legal Data Engineering Platform

CaseFlow is an end-to-end legal data engineering platform for ingesting court opinions, validating and normalizing case data, extracting citation relationships, indexing opinion text for search, and exposing the results through a FastAPI API and React dashboard.

## Highlights

- Resilient Supreme Court opinion ingestion with bounded concurrency, retry logic, and per-document failure isolation
- PostgreSQL-backed case, court, ingestion-job, and citation models
- Idempotent ingestion with content hashing, duplicate detection, and update handling
- Citation extraction and case relationship APIs
- PostgreSQL full-text search using `tsvector`, `tsquery`, ranking, snippets, and a GIN index
- FastAPI REST API with Swagger documentation
- React + TypeScript dashboard served through Nginx
- Docker Compose development stack
- Alembic database migrations
- Pytest coverage for ingestion, citation parsing, API health, search, and source reliability
- GitHub Actions CI

## Architecture

```text
Supreme Court source
        |
        v
Concurrent fetch + PDF parsing
        |
        v
Normalize / validate / hash / deduplicate
        |
        v
PostgreSQL
  |            |
  |            +--> Citation extraction
  |
  +--> Full-text GIN index
        |
        v
FastAPI REST API
        |
        v
Nginx + React dashboard
```

## Demo

### CaseFlow Dashboard

CaseFlow provides ranked full-text search across legal opinions, citation intelligence, system-health visibility, and an end-to-end view of the ingestion pipeline.

![CaseFlow Dashboard](docs/images/caseflow-dashboard.png)

### FastAPI API

The backend exposes case, citation, search, court, and health endpoints through FastAPI with interactive OpenAPI documentation.

![CaseFlow API Documentation](docs/images/caseflow-api-docs.png)