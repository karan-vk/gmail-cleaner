# AGENTS.md - Gmail Service Guide

## OVERVIEW
Core business logic for Gmail operations. Modular design with shared helpers.

## STRUCTURE
```text
app/services/gmail/
├── __init__.py    # Facade (exports cleaner API)
├── helpers.py     # Shared logic (Query builder, Batch headers)
├── scan.py        # Email scanning (pagination, batching)
├── delete.py      # [COMPLEX] Scan & Delete logic
├── archive.py     # Archive operations
├── labels.py      # Label management
└── ...            # Other specific operations
```

## PATTERNS
- **State**: Updates `app.core.state` global variables for progress.
- **Auth**: `get_gmail_service()` retrieves the authenticated client.
- **Batching**: Uses `batch = service.new_batch_http_request()` for performance.
- **Status**: Each module has a `get_*_status()` function.

## CONVENTIONS
- **Queries**: Use `build_gmail_query()` from `helpers.py`.
- **Error Handling**: Catch exceptions, log, and update state to `error`.
- **Pagination**: Handle `nextPageToken` in `while` loops.

## COMPLEXITY
- **delete.py**: Contains both scanning (for deletion candidates) and deletion logic.
- **Batch Limits**: Gmail API has limits (100 reqs/batch). Respect them.

## DEPENDENCIES
- `app.services.auth`: For `get_gmail_service`.
- `app.core.state`: For progress tracking.
