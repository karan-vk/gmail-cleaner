# Contributing to Gmail Cleaner

Thanks for your interest in contributing! 🎉

## Getting Started

1. **Fork** the repository
2. **Clone** your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/gmail-cleaner.git
   cd gmail-cleaner
   ```
3. **Create a branch** for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Setup

### Prerequisites
- Python 3.9+
- [uv](https://github.com/astral-sh/uv) (recommended) or pip
- Your own Google Cloud OAuth credentials

### Running Locally

```bash
# Install dependencies
uv sync

# Run the app
uv run python main.py
```

The app will be available at http://localhost:8766

### Docker Development

```bash
docker compose up --build
```

## Code Style

- **Python**: Follow PEP 8, use type hints where possible
- **JavaScript**: Use the existing modular pattern (`GmailCleaner.ModuleName`)
- **CSS**: Keep styles in appropriate files under `static/css/`

## Making Changes

### For Bug Fixes
1. Create an issue first (if one doesn't exist)
2. Reference the issue in your PR
3. Add tests if applicable

### For New Features
1. Open a feature request issue to discuss the idea
2. Wait for approval before starting work
3. Keep PRs focused and small

## Pull Request Process

1. Update documentation if needed
2. Test your changes locally
3. Test Docker build if you modified Dockerfile or dependencies
4. Fill out the PR template completely
5. A maintainer will be automatically requested for review via CODEOWNERS on all pull requests

## Branch Naming

- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation changes
- `refactor/` - Code refactoring

## Commit Messages

Use clear, descriptive commit messages:
- `feat: add email size filter`
- `fix: resolve Docker build issue with README`
- `docs: update setup instructions`
- `refactor: split scanner module`

## Questions?

Feel free to open an issue or start a discussion!

---

Thank you for contributing! ❤️
