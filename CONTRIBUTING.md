# Contributing to SPECTOR

Thank you for your interest in contributing to SPECTOR! This document provides guidelines and instructions for contributing.

## Code of Conduct

By participating in this project, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md).

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues. When creating a bug report, include:

- **Clear title and description**
- **Steps to reproduce** the behavior
- **Expected vs actual behavior**
- **Environment details** (OS, Python version, dependencies)
- **Sample data** (if applicable and non-sensitive)

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. Include:

- **Use case** - why is this enhancement needed?
- **Proposed solution** - how should it work?
- **Alternatives considered**
- **Additional context** - screenshots, examples, etc.

### Pull Requests

1. **Fork the repository** and create your branch from `main`
2. **Follow code style** - run `black` and `ruff`
3. **Add tests** for new functionality
4. **Update documentation** as needed
5. **Ensure tests pass** (`pytest`)
6. **Run pre-commit hooks** (`pre-commit run --all-files`)
7. **Write clear commit messages**

## Development Workflow

### Setup Development Environment

```bash
# Clone your fork
git clone https://github.com/YOUR-USERNAME/SPECTOR.git
cd SPECTOR

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install

# Start services
docker compose up -d
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=spector --cov-report=html

# Run specific test file
pytest tests/test_pipeline.py

# Run integration tests
pytest tests/integration/
```

### Code Style

We use:
- **Black** for code formatting
- **Ruff** for linting
- **mypy** for type checking
- **isort** for import sorting

```bash
# Format code
black src/

# Lint
ruff check src/

# Type check
mypy src/

# Fix imports
isort src/

# Or run all at once
pre-commit run --all-files
```

### Commit Message Guidelines

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `test`: Adding or updating tests
- `chore`: Maintenance tasks
- `ci`: CI/CD changes

**Examples**:
```
feat(pipeline): add support for DOCX files

Implements PyDocX parser for Word documents with full formatting preservation.

Closes #123
```

```
fix(embeddings): handle empty document edge case

Added validation to prevent crashes when processing empty PDFs.

Fixes #456
```

## Project Structure

```
SPECTOR/
├── src/python/spector/
│   ├── __init__.py
│   ├── cli.py              # CLI entry point
│   ├── pipeline/           # Document processing
│   ├── agents/             # LangGraph agents
│   ├── kg/                 # Knowledge graph ops
│   ├── embeddings/         # Vector search
│   └── utils/              # Utilities
├── tests/
│   ├── unit/               # Unit tests
│   ├── integration/        # Integration tests
│   └── conftest.py         # Pytest fixtures
├── docs/                   # Documentation
├── scripts/                # Utility scripts
└── pyproject.toml          # Dependencies & config
```

## Coding Standards

### Python

- **Python 3.10+** required
- **Type hints** for all public functions
- **Docstrings** (Google style) for classes and public methods
- **Error handling** - never swallow exceptions silently
- **Logging** - use `logging` module, not `print()`

Example:
```python
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

def process_documents(
    paths: List[str],
    output_dir: Optional[str] = None
) -> int:
    """
    Process a list of documents and extract entities.
    
    Args:
        paths: List of file paths to process
        output_dir: Optional output directory for results
        
    Returns:
        Number of documents successfully processed
        
    Raises:
        ValueError: If paths list is empty
        FileNotFoundError: If output_dir doesn't exist
    """
    if not paths:
        raise ValueError("paths cannot be empty")
    
    logger.info(f"Processing {len(paths)} documents")
    
    # Implementation here
    return len(paths)
```

### Testing

- **Unit tests** for individual functions/classes
- **Integration tests** for cross-component workflows
- **Fixtures** for common test data in `conftest.py`
- **Mocking** for external services (APIs, databases)
- **Coverage** - aim for >80%

Example:
```python
import pytest
from spector.pipeline import DocumentProcessor

@pytest.fixture
def sample_pdf(tmp_path):
    """Create a sample PDF for testing."""
    pdf_path = tmp_path / "test.pdf"
    # Create PDF content
    return pdf_path

def test_process_pdf(sample_pdf):
    """Test PDF processing."""
    processor = DocumentProcessor()
    result = processor.process(sample_pdf)
    
    assert result is not None
    assert result.text != ""
    assert result.entities is not None
```

## Documentation

- **README.md** - keep up-to-date with features
- **ARCHITECTURE.md** - document major design decisions
- **Docstrings** - all public APIs must have docstrings
- **Type hints** - help with IDE autocomplete

## Legal & Ethical Guidelines

### Data Sources

✅ **Allowed**:
- Public government documents
- FOIA releases
- Open-source datasets
- Content you have legal rights to process

❌ **Prohibited**:
- Sealed court records
- Bypassing authentication
- Violating terms of service
- Accessing non-public systems

### Responsible Crawling

- **Respect robots.txt**
- **Rate limiting** (default: 1 req/sec)
- **User-Agent** identifying SPECTOR
- **Comply with ToS**

### Privacy

- **No PII** in code examples or tests
- **Anonymize** sample data
- **Document** data handling practices

## Security

### Reporting Vulnerabilities

**DO NOT** open public issues for security vulnerabilities.

Instead, email security@example.com with:
- Vulnerability description
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

See [SECURITY.md](SECURITY.md) for our security policy.

### Secure Coding

- **Never commit secrets** (API keys, passwords)
- **Validate inputs** to prevent injection attacks
- **Use parameterized queries** for databases
- **Sanitize user input** before display
- **Keep dependencies updated**

## Release Process

1. **Update CHANGELOG.md**
2. **Bump version** in `pyproject.toml`
3. **Tag release** (`git tag v1.0.0`)
4. **Push tags** (`git push --tags`)
5. **Create GitHub release**
6. **Publish to PyPI** (maintainers only)

## Getting Help

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: Questions and community support
- **Documentation**: Check existing docs first
- **Discord/Slack**: (If available) Real-time chat

## Recognition

Contributors are listed in:
- GitHub Contributors page (automatic)
- CHANGELOG.md for significant contributions
- Special thanks in release notes

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to SPECTOR! 🎉
