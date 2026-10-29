# CampusAI: Automated Testing & Quality Assurance

## 1. Test Suite Architecture
The test suite consists of **42 automated unit, integration, and end-to-end tests** executed via `pytest`:

| Test Module | Tests | Description |
|---|---|---|
| `tests/test_config.py` | 1 | Settings, directories, and model environment validation |
| `tests/test_inventory.py`| 2 | ZIP extraction, SHA-256 checks, manifest generation |
| `tests/test_database.py` | 5 | PostgreSQL schema, course lookups, semester tables, credits |
| `tests/test_retrieval.py`| 4 | BM25 search, Dense cosine search, RRF fusion, Cross-Encoder |
| `tests/test_intent.py`   | 6 | Language ID, Normalization, Entity extraction, Multi-intent |
| `tests/test_rag.py`      | 5 | Prompt isolation, citation validation, multi-provider adapter |
| `tests/test_api.py`      | 6 | Health checks, courses, chat, source streaming, auth login |
| `tests/test_website.py`  | 3 | Official website scraper, robots.txt, calendar ingestion |
| `tests/test_scenarios.py`| 10| All 10 PART T real-world academic scenarios |
| **Total** | **42** | **100% Passing (Executed in 59.10s)** |

## 2. Running Automated Tests
```bash
# Run entire test suite
pytest tests/ -v

# Run specific subsystem
pytest tests/test_scenarios.py -v
pytest tests/test_retrieval.py -v
pytest tests/test_api.py -v
```
