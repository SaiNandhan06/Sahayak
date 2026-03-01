# PLAN.md – Sahayak Design & Architecture Notes

## Problem Statement

Indian users receive dozens of SMS transaction alerts daily from banks and UPI apps but lack an easy way to:
1. Parse and categorize those expenses
2. Get personalized spending insights
3. Discover the right fintech tools for their situation

## Architecture

```
User (HTTP client)
        │
        ▼
  FastAPI (main.py)
        │
        ├── schemas.py      → Request/response validation
        ├── history.py      → In-memory SessionHistory manager
        │
        ▼
  rag_chain.py              → Core intelligence
        │
        ├── ChromaDB (chroma_db/)
        │     └── nomic-embed-text (OllamaEmbeddings)
        │           └── Retriever k=3
        │
        ├── PromptTemplate  → {context} + {history} + {input}
        │
        └── OllamaLLM       → qwen2:0.5b (local, private)
```

## Key Design Decisions

### 1. Local-first, Privacy-first
All inference runs on the user's machine via Ollama. No data is sent to any cloud service.

### 2. RAG over Fine-tuning
We use Retrieval-Augmented Generation rather than fine-tuning because:
- The knowledge base (SMS formats, app descriptions, budgeting tips) needs to be updated without retraining
- qwen2:0.5b is a small model; RAG compensates for limited parametric knowledge
- ChromaDB allows hot-reload of documents via re-running `data_generation.py`

### 3. Separate Concerns by Module
| Module | Responsibility |
|---|---|
| `config.py` | All constants, env-overridable |
| `history.py` | Session state management |
| `schemas.py` | API contract (Pydantic) |
| `rag_chain.py` | LLM + retrieval logic |
| `main.py` | HTTP routing only |

### 4. Lazy Singleton Initialization
`_get_vectorstore()` and `_get_llm()` in `rag_chain.py` are lazy-loaded once on first request. This avoids slow startup and makes testing easier via mocking.

### 5. In-Memory Sessions
Sessions are stored in a Python dict — fast and zero-dependency. Trade-off: sessions reset on server restart.
For production: replace with Redis or a persistent store.

## Knowledge Base Design

20 synthetic documents were created across 7 categories:

| Category | Docs |
|---|---|
| Spending categories | 6 |
| Indian bank SMS formats | 4 |
| Budgeting strategies | 3 |
| Fintech app descriptions | 4 |
| Overspend alert logic | 1 |
| Recurring bill prediction | 1 |
| Sample Q&A | 1 |

## Known Limitations

- `qwen2:0.5b` is a very small model; responses may be brief or occasionally imprecise
- No persistent session storage across server restarts
- No authentication or rate limiting (suitable for local/bootcamp use only)
- ChromaDB knowledge base is static until `data_generation.py` is re-run
