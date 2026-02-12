# AGENTS.md - Testing Guide

## OVERVIEW
Pytest suite with `pytest-asyncio` and extensive mocking.

## STRUCTURE
```text
tests/
├── conftest.py              # Shared fixtures (CRITICAL)
├── unit/
│   ├── api/                 # Endpoint tests (TestClient)
│   ├── services/
│   │   ├── auth/            # Auth flow (Mocked)
│   │   └── gmail/           # Gmail logic (Mocked)
│   └── models/              # Pydantic validation
└── integration/             # [EMPTY] Needs implementation
```

## KEY FIXTURES (`conftest.py`)
- `mock_gmail_auth` (autouse):
  - **Mocks**: `os.path.exists`, `builtins.open`, `settings.WEB_AUTH`.
  - **Purpose**: Prevents real file access/browser launch.
- `client`: `FastAPI.testclient.TestClient` for API requests.

## CONVENTIONS
- **Sync/Async**: Use `TestClient` for synchronous API testing.
- **Mocking**: Use `unittest.mock.patch` for external services.
- **Isolation**: Tests MUST NOT require valid `credentials.json`.

## GAPS
- **Integration**: No true integration tests exist.
- **Async**: Direct async service testing is limited.

## COMMANDS
```bash
uv run pytest
uv run pytest --cov=app
```
