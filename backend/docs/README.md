# Backend Documentation

This directory contains documentation for the Django backend of the AI-powered e-commerce optimization platform.

## Contents

- [API Documentation](./api.md) - REST API endpoints and usage
- [Models](./models.md) - Database models and relationships
- [Agents](./agents.md) - Background automation agents
- [Testing](./testing.md) - Testing guidelines and procedures
- [Deployment](./deployment.md) - Deployment and configuration

## Quick Start

For development setup, see the main [README.md](../README.md) in the project root.

## Architecture Overview

The backend is built with Django 5.0 and follows a modular architecture with feature-based apps:

- **core**: Authentication, users, organizations
- **brands**: Brand management and profiles
- **ai**: AI-powered content generation
- **onboarding**: User onboarding workflows
- **shopify**: E-commerce platform integration
- **seo**: Search engine optimization
- **competitors**: Competitive analysis
- **store_templates**: Website templates

## Development Guidelines

### Code Style
- Follow PEP 8 Python style guidelines
- Use Black for code formatting
- Use Ruff for linting
- Write comprehensive docstrings

### Testing
- Write tests for all new features
- Maintain >80% test coverage
- Run tests before committing: `pytest`

### Database Migrations
- Create migrations for model changes: `python manage.py makemigrations`
- Apply migrations: `python manage.py migrate`
- Test migrations in development before deploying

## Support

For questions or issues, please check:
1. This documentation
2. The main project README
3. GitHub issues
4. Team chat
