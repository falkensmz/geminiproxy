# Contributing to GeminiProxy

First off, thank you for considering contributing to GeminiProxy! It's people like you that make GeminiProxy such a great tool.

## Code of Conduct

This project and everyone participating in it is governed by the [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues as you might find out that you don't need to create one. When you are creating a bug report, please include as many details as possible:

* **Use a clear and descriptive title**
* **Describe the exact steps to reproduce the problem**
* **Provide specific examples to demonstrate the steps**
* **Describe the behavior you observed and what behavior you expected**
* **Include screenshots if possible**
* **Include your environment details** (OS, Python version, etc.)

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, please include:

* **Use a clear and descriptive title**
* **Provide a detailed description of the suggested enhancement**
* **Provide specific examples to demonstrate the enhancement**
* **Describe the current behavior and expected behavior**
* **Explain why this enhancement would be useful**

### Pull Requests

1. Fork the repo and create your branch from `main`
2. If you've added code that should be tested, add tests
3. If you've changed APIs, update the documentation
4. Ensure the test suite passes
5. Make sure your code follows the existing style
6. Issue that pull request!

## Development Setup

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/GeminiProxy.git
   cd GeminiProxy
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements-dev.txt
   pip install -e .
   ```

4. **Set up pre-commit hooks**
   ```bash
   pre-commit install
   ```

## Development Workflow

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write your code
   - Add tests for new functionality
   - Update documentation as needed

3. **Run tests**
   ```bash
   pytest tests/
   ```

4. **Check code style**
   ```bash
   black geminiproxy/
   flake8 geminiproxy/
   isort geminiproxy/
   ```

5. **Commit your changes**
   ```bash
   git add .
   git commit -m "Add feature: description of your changes"
   ```

6. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create a Pull Request**
   - Go to the original repository
   - Click "New Pull Request"
   - Select your fork and branch
   - Fill in the PR template
   - Submit!

## Testing

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=geminiproxy

# Run specific test file
pytest tests/test_client.py

# Run with verbose output
pytest -v
```

### Writing Tests
- Place tests in the `tests/` directory
- Name test files with `test_` prefix
- Use descriptive test function names
- Include both positive and negative test cases
- Mock external dependencies

## Code Style

We use several tools to maintain code quality:

- **Black** for code formatting
- **Flake8** for linting
- **isort** for import sorting
- **mypy** for type checking

### Style Guide
- Follow PEP 8
- Use type hints where possible
- Write descriptive variable names
- Add docstrings to all functions and classes
- Keep functions small and focused
- Comment complex logic

## Documentation

- Update README.md for user-facing changes
- Add docstrings following Google style
- Update API documentation for new endpoints
- Include examples for new features

## Commit Messages

- Use present tense ("Add feature" not "Added feature")
- Use imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit first line to 72 characters
- Reference issues and pull requests

### Examples
```
Add rate limiting to batch processing
Fix memory leak in cache system
Update documentation for new API endpoints
Refactor database connection handling
```

## Release Process

1. Update version in `setup.py` and `__init__.py`
2. Update CHANGELOG.md
3. Create a release branch
4. Run full test suite
5. Create pull request to main
6. Tag release after merge
7. Build and publish to PyPI

## Questions?

Feel free to open an issue with your question or reach out to the maintainers.

## Recognition

Contributors will be recognized in:
- The project README
- Release notes
- Contributors page

Thank you for contributing to GeminiProxy! 🚀