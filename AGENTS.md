# AGENTS.md - Development Guide

**Generated:** Thu, Feb 12, 2026
**Commit:** {DYNAMIC}
**Branch:** main

## OVERVIEW
Privacy-focused Gmail cleanup tool using **FastAPI** (Python 3.9+) and **Vanilla JS**. Runs locally/Docker, no external database.

## STRUCTURE
```
.
├── app/               # FastAPI backend
│   ├── api/           # Routes (actions.py, status.py)
│   ├── core/          # Config & State (Global variables)
│   ├── models/        # Pydantic schemas
│   └── services/      # Business logic
│       ├── auth.py    # OAuth flow & Credential mgmt (God Object)
│       └── gmail/     # Gmail API operations (Scan, Delete, Archive)
├── static/            # Frontend (Vanilla JS)
│   ├── js/            # Logic (Module pattern, global namespace)
│   └── css/           # Styles
├── templates/         # HTML (Jinja2)
└── tests/             # Pytest suite
    ├── unit/          # Isolated tests (Mocked)
    └── integration/   # [EMPTY] Missing integration tests
```

## WHERE TO LOOK
| Task | Location | Notes |
|------|----------|-------|
| **Auth/Login** | `app/services/auth.py` | Handles OAuth, tokens, local server. Complex. |
| **Email Logic** | `app/services/gmail/` | Modular operations (scan, delete, etc.). |
| **Frontend UI** | `static/js/` | Ad-hoc framework. `main.js` orchestrates. |
| **State** | `app/core/state.py` | Global thread-safe state for async tasks. |
| **API Routes** | `app/api/` | `actions.py` (POST), `status.py` (GET). |
| **Config** | `app/core/config.py` | Settings via Pydantic (`.env`). |

## CODE MAP (Key Symbols)
| Symbol | Type | Location | Role |
|--------|------|----------|------|
| `GmailService` | Class | `app/services/auth.py` | Wrapper for Gmail API resource. |
| `get_gmail_service` | Func | `app/services/auth.py` | **CRITICAL**. Retrieves/refreshes auth. |
| `process_scan` | Func | `app/services/gmail/scan.py` | Core scanning logic. |
| `GmailCleaner` | Obj | `static/js/main.js` | Global frontend namespace (State/UI). |
| `app` | Var | `app/main.py` | FastAPI application instance. |

## CONVENTIONS
- **State**: Backend uses `app.core.state` global variables for progress tracking.
- **Frontend**: "Module Pattern" with global `GmailCleaner`. No build step.
- **Async**: Backend is async (FastAPI), but uses `threading` for background tasks.
- **Testing**:
  - `pytest` with `pytest-asyncio`.
  - **Mocks**: Aggressive mocking of `credentials.json` in `conftest.py`.
  - **Fixtures**: `mock_gmail_auth` (autouse) prevents real auth in tests.

## ANTI-PATTERNS (THIS PROJECT)
- **NO SECRETS**: NEVER commit `credentials.json`, `token.json`, or `.env`.
- **No `try/except`**: Use `HTTPException` or custom exceptions.
- **Frontend Coupling**: Logic/UI tightly coupled in `labels.js`/`delete.js`.
- **Global State**: Frontend relies on global `window.GmailCleaner`.

## COMMANDS
```bash
# Dev
uv sync
uv run python main.py

# Test
uv run pytest
uv run pytest tests/unit/services/auth/

# Lint
uv run ruff check .
uv run pyright
```

## NOTES
- **Auth Flow**: Uses a local server callback. Docker requires port mapping.
- **Data Persistence**: `token.json` stored in `./data/` (Docker volume).
- **Concurrency**: `app/services/gmail` uses batch requests (performance).
