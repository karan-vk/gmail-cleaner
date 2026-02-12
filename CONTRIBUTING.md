# Contributing to Gmail Cleaner

Thanks for your interest in contributing! This document will help you get started.

## Table of Contents

- [Quick Start](#quick-start)
- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Making Changes](#making-changes)
- [Pull Request Guidelines](#pull-request-guidelines)
- [Code Style](#code-style)
- [Testing](#testing)
- [Documentation](#documentation)
- [Community](#community)

---

## Quick Start

```bash
# 1. Fork and clone
git clone https://github.com/YOUR_USERNAME/gmail-cleaner.git
cd gmail-cleaner

# 2. Install dependencies
uv sync

# 3. Set up pre-commit hooks (optional but recommended)
uv run pre-commit install

# 4. Run the app
uv run python main.py

# 5. Run tests
uv run pytest
```

---

## Development Setup

### Prerequisites

- **Python 3.9+** ([Download](https://www.python.org/downloads/))
- **uv** ([Install guide](https://docs.astral.sh/uv/getting-started/installation/))
- **Google Cloud OAuth credentials** (your own - see README)

### Local Development

```bash
# Install all dependencies including dev tools
uv sync --group dev

# Run the application
uv run python main.py

# Open http://localhost:8766
```

### Docker Development

```bash
# Build and run with Docker
docker compose up --build

# Open http://localhost:8766
```

### IDE Setup

**Recommended VS Code extensions:**

- Python (Microsoft)
- Pylance
- Ruff

**Recommended settings:**

```json
{
  "python.linting.enabled": true,
  "python.formatting.provider": "none",
  "[python]": {
    "editor.formatOnSave": true,
    "editor.defaultFormatter": "charliermarsh.ruff"
  }
}
```

---

## Project Structure

```
gmail-cleaner/
├── app/                    # Backend (FastAPI)
│   ├── api/               # API routes
│   │   ├── actions.py     # POST endpoints
│   │   └── status.py      # GET endpoints
│   ├── core/              # Config & state
│   ├── models/            # Pydantic schemas
│   └── services/          # Business logic
│       ├── auth.py        # OAuth authentication
│       └── gmail/         # Gmail API operations
├── static/                 # Frontend
│   ├── js/                # JavaScript modules
│   └── css/               # Styles
├── templates/              # HTML templates (Jinja2)
├── tests/                  # Test suite
│   ├── unit/              # Unit tests
│   └── integration/       # Integration tests
├── .github/               # GitHub config
│   ├── workflows/         # CI/CD
│   └── ISSUE_TEMPLATE/    # Issue templates
├── main.py                 # Application entry point
├── pyproject.toml         # Project config
└── docker-compose.yml     # Docker config
```

For a detailed architecture overview, see [ARCHITECTURE.md](ARCHITECTURE.md).

---

## Making Changes

### Before You Start

1. **Check existing issues** - Someone might already be working on it
2. **Open a discussion** - For major changes, discuss the approach first
3. **Create a branch** - Use descriptive names like `feature/bulk-archive` or `fix/oauth-timeout`

### Branch Naming Convention

| Type | Example |
|------|---------|
| Feature | `feature/dark-mode` |
| Bug fix | `fix/token-refresh-error` |
| Documentation | `docs/update-readme` |
| Refactor | `refactor/auth-service` |
| Test | `test/integration-tests` |

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

**Types:**

| Type | Description |
|------|-------------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `style` | Code style (formatting, etc.) |
| `refactor` | Code refactoring |
| `test` | Adding/updating tests |
| `chore` | Maintenance tasks |

**Examples:**

```
feat(ui): add dark mode toggle
fix(auth): handle token refresh on expiry
docs(setup): clarify OAuth redirect URI setup
test(scan): add tests for filter combinations
```

---

## Pull Request Guidelines

### Before Submitting

- [ ] Tests pass locally: `uv run pytest`
- [ ] Code follows style guidelines: `uv run ruff check .`
- [ ] Type checking passes: `uv run pyright`
- [ ] Documentation updated (if needed)
- [ ] Commit messages follow convention

### PR Checklist

Your PR should include:

1. **Description** - What does this change do?
2. **Related Issues** - Link any related issues
3. **Testing** - How was this tested?
4. **Screenshots** - For UI changes

### PR Template

```markdown
## Description
[What does this PR do?]

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
[How did you test this?]

## Screenshots (if applicable)
[Add screenshots here]

## Checklist
- [ ] Tests pass locally
- [ ] Code follows style guidelines
- [ ] Documentation updated
```

### Review Process

1. All PRs require review from a maintainer
2. CI checks must pass
3. Address review feedback
4. Squash and merge when approved

---

## Code Style

### Python

- **Style**: PEP 8
- **Linter**: Ruff
- **Formatter**: Ruff format
- **Types**: Type hints encouraged but not required

**Run linting:**

```bash
# Check for issues
uv run ruff check .

# Auto-fix issues
uv run ruff check . --fix
```

### JavaScript

- **Style**: Standard JavaScript
- **No build step**: Keep it simple, vanilla JS
- **Module pattern**: Use the existing `GmailCleaner` namespace

### Key Conventions

| Convention | Example |
|------------|---------|
| Function names | `snake_case` for Python, `camelCase` for JS |
| Constants | `UPPER_SNAKE_CASE` |
| Private methods | Prefix with `_` in Python |
| Error handling | Raise `HTTPException` or custom exceptions |

---

## Testing

### Running Tests

```bash
# All tests
uv run pytest

# Specific test file
uv run pytest tests/unit/services/auth/test_oauth_flow.py

# With coverage
uv run pytest --cov=app --cov-report=html

# Verbose output
uv run pytest -v
```

### Test Organization

```
tests/
├── unit/              # Fast, isolated tests
│   ├── api/           # API endpoint tests
│   ├── models/        # Model validation tests
│   └── services/      # Service logic tests
├── integration/       # Slower, full-stack tests
└── conftest.py        # Shared fixtures
```

### Writing Tests

**Unit tests:**
- Mock external dependencies (Gmail API, file system)
- Test one thing per test
- Use descriptive test names

```python
def test_scan_emails_filters_by_sender(mock_gmail_service):
    """Test that scan filters emails by sender address."""
    # Arrange
    filters = {"sender": "test@example.com"}
    
    # Act
    result = scan_emails(filters=filters)
    
    # Assert
    assert all(msg["sender"] == "test@example.com" for msg in result)
```

---

## Documentation

### When to Update Docs

- New features → Update README and ARCHITECTURE
- API changes → Update API documentation
- Setup changes → Update README setup section
- New commands → Update AGENTS.md

### Documentation Files

| File | Purpose |
|------|---------|
| `README.md` | User-facing overview and setup |
| `ARCHITECTURE.md` | Technical architecture details |
| `CONTRIBUTING.md` | Contribution guidelines |
| `SECURITY.md` | Security policy |
| `ROADMAP.md` | Project direction |
| `AGENTS.md` | AI assistant context |

---

## Community

### Getting Help

- **Issues**: [GitHub Issues](https://github.com/Gururagavendra/gmail-cleaner/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Gururagavendra/gmail-cleaner/discussions)
- **Security**: See [SECURITY.md](SECURITY.md)

### Code of Conduct

We follow the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). Be respectful and inclusive.

### Recognition

Contributors are recognized in:

- Release notes for significant contributions
- README acknowledgments for major features
- GitHub Contributors page

---

## Quick Reference

| Task | Command |
|------|---------|
| Install dependencies | `uv sync` |
| Run app | `uv run python main.py` |
| Run tests | `uv run pytest` |
| Run tests with coverage | `uv run pytest --cov=app` |
| Lint code | `uv run ruff check .` |
| Fix lint issues | `uv run ruff check . --fix` |
| Type check | `uv run pyright` |
| Build Docker | `docker compose up --build` |

---

Thank you for contributing! Your help makes Gmail Cleaner better for everyone.
