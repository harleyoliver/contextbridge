# ContextBridge

> AI-powered enterprise data integration toolkit

ContextBridge connects disparate enterprise data sources (CRM, ticketing, HR systems), normalises the data, and layers a multi-agent AI interface on top — enabling natural-language queries, automated summaries, and cross-system insights.

## Architecture

_Coming in Week 5 — Excalidraw diagram_

## Quick start

```bash
# Start PostgreSQL
docker compose up postgres -d

# Install dependencies (from /backend)
uv pip install -e ".[dev]"

# Run the API
uvicorn app.main:app --reload

# Visit http://localhost:8000/docs
```

## Tech stack

| Layer | Technology |
|---|---|
| API | FastAPI + Python 3.12 |
| Database | PostgreSQL + SQLAlchemy 2.0 (async) |
| AI / RAG | LangChain + LangGraph + ChromaDB _(Week 3)_ |
| Quick demos | Streamlit _(Week 4)_ |
| Frontend | React + TypeScript _(Week 4)_ |
| Deploy | Docker Compose + Railway |

## Development

```bash
# Lint
ruff check .

# Test
pytest tests/ -v
```

## Roadmap

- [x] Week 1–2: FastAPI backend + PostgreSQL data ingestion
- [ ] Week 3: RAG pipeline + LangGraph agent
- [ ] Week 4: Docker Compose + Streamlit dashboard
- [ ] Week 5: Multi-agent orchestration + RFC doc
- [ ] Week 6: Public deployment + demo video
