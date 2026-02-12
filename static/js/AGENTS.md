# AGENTS.md - Frontend Guide

## OVERVIEW
Vanilla JavaScript frontend using a "Module Pattern" architecture. No framework, no build step.

## STRUCTURE
```
static/js/
├── main.js        # Entry point (DOMContentLoaded, Event listeners)
├── ui.js          # Shared UI utilities (Toast, View switching)
├── auth.js        # Auth logic (Sign in/out, UI updates)
├── labels.js      # [LARGE] Label management (Fetch + UI rendering)
├── delete.js      # [LARGE] Deletion logic (Fetch + UI rendering)
├── scanner.js     # Scanning logic
├── filters.js     # Filter UI logic
└── markread.js    # Mark as read logic
```

## ARCHITECTURE
- **Global Namespace**: `window.GmailCleaner` is the single source of truth.
- **State**: Stored in `GmailCleaner.results`, `GmailCleaner.scanning`, etc.
- **Modules**: Each file extends `GmailCleaner` (e.g., `GmailCleaner.Labels`).
- **Initialization**: `main.js` calls `init()` methods of other modules.

## CONVENTIONS
- **DOM**: Use `document.getElementById` or `querySelector`.
- **Events**:
  - **Static**: `addEventListener` in `main.js`.
  - **Dynamic**: Inline `onclick` in template literals (requires global scope).
- **Updates**: Direct DOM manipulation (e.g., `element.innerHTML = ...`).
- **Polling**: Manual `setInterval` for background task progress.

## ANTI-PATTERNS
- **No Imports**: Do NOT use `import`/`export` (not supported without build).
- **No Frameworks**: Do NOT add React, Vue, or jQuery. Keep it vanilla.
- **Duplication**: Avoid copying "Overlay" or "Polling" logic (use `ui.js`).

## COMMON TASKS
| Task | implementation |
|------|----------------|
| **Add View** | Add HTML to `index.html`, add nav in `main.js`, add show() in `ui.js`. |
| **New API Call** | Use `fetch('/api/...')`, handle errors, update UI. |
| **Show Toast** | `GmailCleaner.UI.showToast(message, type)`. |
