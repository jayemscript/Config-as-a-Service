# Contributing to Config-as-a-Service

Thank you for your interest in contributing! This document provides guidelines for getting involved.

## Getting Started

### Prerequisites

- Python 3.11 or higher
- Git
- Familiarity with FastAPI and SQLAlchemy

### Development Setup

1. **Fork the repository**

   ```bash
   # On GitHub: click "Fork"
   ```

2. **Clone your fork**

   ```bash
   git clone https://github.com/YOUR_USERNAME/Config-as-a-Service.git
   cd Config-as-a-Service
   ```

3. **Create a virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

5. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Generate keys:
   python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
   # Update .env with generated ENCRYPTION_KEY and JWT_SECRET_KEY
   ```

---

## Development Workflow

### 1. Create a Feature Branch

```bash
git checkout -b feature/my-feature
# or for fixes:
git checkout -b fix/issue-number
```

### 2. Make Changes

- Keep commits atomic and descriptive
- Follow Python style guidelines (see below)
- Add tests for new features
- Update documentation if needed

### 3. Run Tests

```bash
pytest
pytest --cov=src/caas  # With coverage
```

### 4. Test Locally

```bash
# Start the API
python -m src.caas.main

# In another terminal, generate a token
python -m src.caas.cli auth generate-token

# Test CLI commands
python -m src.caas.cli config list
python -m src.caas.cli config create --app-name test-app --env DEVELOPMENT --inline '{"KEY":"value"}'
```

### 5. Commit and Push

```bash
git add .
git commit -m "Clear, descriptive commit message"
git push origin feature/my-feature
```

### 6. Open a Pull Request

- Go to GitHub and create a PR from your fork
- Fill in the PR template
- Reference related issues (e.g., "Fixes #123")

---

## Code Style

### Python Standards

- **Formatter:** Black (line length: 100)
- **Linter:** Flake8
- **Type Hints:** Use for function signatures

```bash
# Format code
black src/ tests/

# Check style
flake8 src/ tests/

# Type checking (future)
mypy src/
```

### Naming Conventions

- `Classes`: PascalCase
- `Functions/methods`: snake_case
- `Constants`: UPPER_SNAKE_CASE
- `Private members`: `_leading_underscore`

### Docstrings

Use Google-style docstrings:

```python
def create_configuration(name: str) -> Configuration:
    """
    Create a new configuration.

    Args:
        name: Configuration name

    Returns:
        Created Configuration object

    Raises:
        ValueError: If name is invalid
    """
    pass
```

---

## Testing Guidelines

### Test Structure

```
tests/
├── unit/
│   ├── test_encryption.py
│   ├── test_models.py
│   └── test_auth.py
├── integration/
│   └── test_api.py
└── cli/
    └── test_commands.py
```

### Writing Tests

- Use `pytest` framework
- Mock external dependencies
- Aim for >80% coverage for new code
- Test both success and error paths

```python
def test_create_configuration(db: Session):
    """Test successful configuration creation."""
    config = Configuration(
        app_name="test",
        environment_type=EnvironmentType.DEVELOPMENT,
        values="{}"
    )
    db.add(config)
    db.commit()

    assert config.id is not None
    assert config.version == 1
```

---

## Documentation

### Adding Features

1. Update `README.md` if user-facing
2. Update `GUIDE.md` if it affects setup/usage
3. Add docstrings to code
4. Update API schemas if endpoints change

### Documentation Format

- Use Markdown
- Keep lines <100 characters
- Use code blocks with language tags
- Include examples

---

## Commit Message Format

Follow conventional commits:

```
type(scope): subject

body

footer
```

**Types:**

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `test`: Tests
- `refactor`: Code refactoring
- `chore`: Build/dependency updates
- `ci`: CI/CD changes

**Examples:**

```
feat(api): add POST /cass/create endpoint

Implement configuration creation with Fernet encryption.
Validates app_name uniqueness per environment.

Closes #45
```

```
fix(cli): handle missing token gracefully

Show helpful error message when token is not found.
```

---

## Issue Labels

When creating issues, use labels:

- `bug`: Something isn't working
- `enhancement`: New feature or improvement
- `documentation`: Improvements or additions to docs
- `good first issue`: Good for newcomers
- `security`: Security concern
- `help wanted`: Need assistance

---

## Code Review Process

### For Reviewers

1. Check code style and tests
2. Verify functionality matches description
3. Ask clarifying questions if needed
4. Approve or request changes

### For Contributors

- Respond to feedback promptly
- Don't be discouraged by requests
- Update PR based on feedback
- Re-request review after changes

---

## Release Process

1. Update version in `src/caas/__init__.py`
2. Update `CHANGELOG.md` (future)
3. Create git tag: `git tag v0.1.0`
4. Push tag: `git push origin v0.1.0`
5. GitHub Actions builds and releases

---

## Areas We Need Help

- [ ] Adding more comprehensive tests
- [ ] Docker and docker-compose setup
- [ ] GitHub Actions CI/CD workflow
- [ ] Pre-built releases (wheel, exe)
- [ ] Performance optimization
- [ ] Additional documentation
- [ ] Example projects/integrations
- [ ] Security hardening
- [ ] PostgreSQL support

---

## Code of Conduct

This project adheres to a [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you're expected to uphold it.

---

## Questions?

- Open a discussion on GitHub
- Check existing issues and PRs
- Read the [GUIDE.md](GUIDE.md)

---

## License

By contributing, you agree your work is licensed under the MIT License.

Thank you for contributing! 🎉
