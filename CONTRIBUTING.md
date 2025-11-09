# Contributing to AI-Powered E-commerce Onboarding System

Thank you for your interest in contributing! This document provides guidelines for contributing to the project safely and effectively.

## Table of Contents

- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Safe Development Checklist](#safe-development-checklist)
- [Code Standards](#code-standards)
- [Testing Requirements](#testing-requirements)
- [Security Guidelines](#security-guidelines)
- [Commit Message Format](#commit-message-format)
- [Pull Request Process](#pull-request-process)

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 14+
- Redis 7+
- Docker and Docker Compose

### Setup Development Environment

```bash
# Clone the repository
git clone <repository-url>
cd monorepo

# Install pre-commit hooks
pip install pre-commit
pre-commit install

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate

# Frontend setup
cd ../frontend
npm install  # or pnpm install

# Copy environment files
cp .env.example .env
# Edit .env with your local settings
```

## Development Workflow

1. **Create a feature branch**
   ```bash
   git checkout -b feat/your-feature-name
   ```

2. **Make your changes**
   - Write code following our standards
   - Add/update tests
   - Update documentation

3. **Run tests locally**
   ```bash
   # Backend tests
   cd backend
   pytest

   # Frontend tests
   cd frontend
   npm test
   ```

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add amazing feature"
   ```

5. **Push and create PR**
   ```bash
   git push origin feat/your-feature-name
   ```

## Safe Development Checklist

Before committing code, ensure you:

- [ ] **No secrets in code** - API keys, passwords, tokens should be in environment variables
- [ ] **No large files** - Files over 1MB should not be committed (use .gitignore)
- [ ] **No private keys** - Never commit SSH keys, SSL certificates, or private keys
- [ ] **Environment variables documented** - Add new env vars to .env.example
- [ ] **Migrations included** - Django migrations are committed with model changes
- [ ] **Tests pass** - All tests pass locally
- [ ] **Schema validation** - JSON schemas validate correctly
- [ ] **No commented code** - Remove or properly document commented code
- [ ] **No TODO/FIXME in production** - Resolve or create issues for TODOs

## Code Standards

### Python (Backend)

- **Style**: Follow PEP 8
- **Formatter**: Black (line length 100)
- **Linter**: Flake8
- **Type hints**: Use type hints for function signatures
- **Docstrings**: Use Google-style docstrings

```python
def process_onboarding_data(session_id: str, data: Dict[str, Any]) -> OnboardingSession:
    """
    Process onboarding data for a session.

    Args:
        session_id: UUID of the onboarding session
        data: Dictionary containing onboarding form data

    Returns:
        Updated OnboardingSession instance

    Raises:
        ValidationError: If data validation fails
    """
    ...
```

### TypeScript/JavaScript (Frontend)

- **Style**: Follow Airbnb style guide
- **Formatter**: Prettier
- **Linter**: ESLint
- **Type safety**: Use TypeScript for all new code

### JSON Schemas

- Follow JSON Schema Draft 7 specification
- Include descriptions for all fields
- Validate with management command: `python manage.py validate_schemas`

## Testing Requirements

### Test Coverage

- **Minimum coverage**: 95%
- **Required tests**:
  - Unit tests for all business logic
  - Integration tests for API endpoints
  - Schema validation tests
  - Permission/authorization tests

### Running Tests

```bash
# Backend - all tests
cd backend
pytest

# Backend - specific test file
pytest tests/test_onboarding_session.py

# Backend - with coverage
pytest --cov=. --cov-report=html

# Frontend - all tests
cd frontend
npm test

# Frontend - with coverage
npm test -- --coverage
```

### Test Structure

```python
# tests/test_feature.py
import pytest

@pytest.fixture
def setup_data(db):
    """Fixture description"""
    return SomeModel.objects.create(...)

@pytest.mark.django_db
class TestFeature:
    """Test suite for feature"""

    def test_specific_behavior(self, setup_data):
        """Test that specific behavior works correctly"""
        # Arrange
        ...
        # Act
        ...
        # Assert
        assert ...
```

## Security Guidelines

### Authentication & Authorization

- Always use Django's authentication system
- Check permissions in views using `permission_classes`
- Never trust client-side validation alone
- Validate all input data

### Data Protection

- Use environment variables for sensitive data
- Encrypt sensitive data at rest
- Use HTTPS for all API communication
- Implement rate limiting on sensitive endpoints

### Input Validation

- Validate all user input
- Use Django ORM to prevent SQL injection
- Sanitize data before storing
- Use JSON schema validation for structured data

### GDPR Compliance

- Record user consent with timestamp and IP
- Provide consent revocation mechanism
- Implement data deletion within 30 days
- Maintain audit trail for compliance

### Common Vulnerabilities to Avoid

❌ **Don't do this:**
```python
# SQL injection vulnerability
User.objects.raw(f"SELECT * FROM users WHERE email = '{email}'")

# XSS vulnerability
return HttpResponse(f"<h1>Welcome {user_input}</h1>")

# Hardcoded secrets
API_KEY = "sk_live_12345abcdef"
```

✅ **Do this instead:**
```python
# Use ORM
User.objects.filter(email=email)

# Escape output
return HttpResponse(format_html("<h1>Welcome {}</h1>", user_input))

# Use environment variables
API_KEY = os.environ.get('API_KEY')
```

## Commit Message Format

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### Examples

```
feat(onboarding): add consent management system

Implement GDPR-compliant consent recording with:
- UserConsent model with audit trail
- Consent blocking logic for scans
- Consent revocation support

Closes #123
```

```
fix(scan): handle timeout errors gracefully

Add proper error handling for scan timeouts with retry logic.
Scans now retry up to 3 times with exponential backoff.

Fixes #456
```

## Pull Request Process

### Before Creating PR

1. Ensure all tests pass
2. Update documentation
3. Add entry to CHANGELOG.md
4. Rebase on latest main branch
5. Run pre-commit hooks

### PR Checklist

Create PR with this checklist:

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing completed
- [ ] All tests pass

## Security
- [ ] No secrets committed
- [ ] Input validation added
- [ ] Authorization checks added
- [ ] OWASP top 10 considered

## Documentation
- [ ] Code comments added
- [ ] API documentation updated
- [ ] README updated (if needed)
- [ ] CHANGELOG updated

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] No console.log or debug statements
- [ ] No commented-out code
- [ ] Migration files included (if needed)
```

### Review Process

1. Automated checks must pass (CI/CD)
2. At least one code review required
3. Security review for authentication/authorization changes
4. Architecture review for significant changes

### Merging

- Use "Squash and merge" for feature branches
- Delete branch after merge
- Ensure CI/CD passes on main branch

## Getting Help

- **Questions**: Create a GitHub Discussion
- **Bug Reports**: Open a GitHub Issue
- **Security Issues**: Email security@example.com (do not create public issue)
- **Feature Requests**: Open a GitHub Issue with `feature` label

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Focus on constructive feedback
- Follow project guidelines
- Report unacceptable behavior

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.

---

Thank you for contributing to make this project better! 🎉
