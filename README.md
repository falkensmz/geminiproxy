# GeminiProxy 🚀

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

A powerful Python wrapper and REST API for Google's Gemini CLI, designed to seamlessly manage free tier limitations with intelligent rate limiting, caching, and enterprise-ready features.

## ✨ Features

- 🔒 **Smart Rate Limiting** - Automatic tracking and management of the 1000 requests/hour limit
- 💾 **Response Caching** - Reduce redundant API calls with intelligent TTL-based caching
- 🔄 **Retry Logic** - Automatic retries with exponential backoff for failed requests
- ⚡ **Async Processing** - Queue requests for non-blocking background processing
- 🌐 **REST API** - Full-featured HTTP API with Flask and CORS support
- 📊 **Usage Analytics** - Comprehensive tracking and historical statistics
- 🎯 **Batch Processing** - Efficiently process multiple prompts with progress tracking
- 🔧 **CLI Tool** - Feature-rich command-line interface for all operations
- 🐳 **Docker Support** - Ready-to-deploy containerized solution
- 📝 **Extensive Logging** - Detailed logging for debugging and monitoring

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/falkensmz/GeminiProxy.git
cd GeminiProxy

# Install with pip
pip install -e .

# Or install from PyPI (when published)
pip install geminiproxy
```

### Basic Usage

#### Command Line

```bash
# Send a simple prompt
geminiproxy "Explain quantum computing in simple terms"

# Check usage statistics
geminiproxy --stats

# Process multiple prompts
geminiproxy --batch prompts.txt --output results.json

# Start the REST API server
geminiproxy --server --port 5000
```

#### Python API

```python
from geminiproxy import GeminiClient

# Initialize client
client = GeminiClient()

# Send a prompt
response = client.prompt("Write a haiku about Python")
if response["success"]:
    print(response["output"])

# Check usage
stats = client.get_usage()
print(f"Remaining requests: {stats['remaining_this_hour']}")

# Batch processing
prompts = ["What is AI?", "Explain ML", "Define NLP"]
results = client.batch_prompts(prompts)
```

#### REST API

```bash
# Start the server
geminiproxy --server

# Send a prompt
curl -X POST http://localhost:5000/prompt \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Hello, Gemini!"}'

# Check usage
curl http://localhost:5000/usage

# Async request
curl -X POST http://localhost:5000/prompt/async \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Complex analysis task"}'
```

## 📚 Documentation

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API documentation |
| `/health` | GET | Health check with usage stats |
| `/usage` | GET | Detailed usage statistics |
| `/prompt` | POST | Send prompt (synchronous) |
| `/prompt/async` | POST | Queue prompt (asynchronous) |
| `/job/<id>` | GET | Check async job status |
| `/batch` | POST | Process multiple prompts |
| `/stream` | POST | Stream responses (SSE) |
| `/jobs` | GET | List all jobs |
| `/cache/clear` | POST | Clear response cache |
| `/stats/history` | GET | Historical usage data |

### Configuration

```python
from geminiproxy import GeminiClient

client = GeminiClient(
    auto_approve=True,        # Auto-approve tool calls
    checkpointing=True,       # Enable checkpointing
    max_retries=3,           # Retry attempts
    rate_limit_per_hour=950, # Conservative limit
    cache_ttl=3600,          # Cache TTL in seconds
    timeout=300              # Command timeout
)
```

## 🐳 Docker Deployment

### Using Docker

```bash
# Build the image
docker build -t geminiproxy .

# Run the container
docker run -p 5000:5000 geminiproxy

# With environment variables
docker run -p 5000:5000 \
  -e RATE_LIMIT=900 \
  -e AUTO_APPROVE=true \
  geminiproxy
```

### Using Docker Compose

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## 🏗️ Architecture

```
GeminiProxy/
├── geminiproxy/
│   ├── __init__.py       # Package initialization
│   ├── client.py         # Core client implementation
│   ├── server.py         # REST API server
│   ├── database.py       # SQLite rate limiting
│   ├── exceptions.py     # Custom exceptions
│   └── cli.py           # CLI interface
├── tests/               # Test suite
├── docs/               # Documentation
├── examples/           # Usage examples
└── docker/            # Docker configuration
```

## 🔧 Advanced Features

### Rate Limiting

The system tracks API usage in a local SQLite database (`~/.geminiproxy/rate_limit.db`) and enforces a conservative limit of 950 requests/hour. When limits are reached:

- Synchronous calls return error with wait time
- Async calls are automatically queued
- Batch processing pauses intelligently

### Caching Strategy

Responses are cached with configurable TTL:
- In-memory cache for fast retrieval
- MD5-based cache keys
- Automatic cache invalidation
- Manual cache clearing available

### Error Handling

Comprehensive error handling with:
- Custom exception hierarchy
- Detailed error messages
- Automatic retry logic
- Graceful degradation

## 📊 Monitoring & Analytics

Track your usage with built-in analytics:

```bash
# View current usage
geminiproxy --stats

# Get historical data (API)
curl http://localhost:5000/stats/history?days=30

# Clean old data
geminiproxy --cleanup
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Google for providing the Gemini CLI tool
- The Python community for excellent libraries
- All contributors and users of this project

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/falkensmz/GeminiProxy/issues)
- **Discussions**: [GitHub Discussions](https://github.com/falkensmz/GeminiProxy/discussions)
- **Email**: contact@falkensmz.dev

## 🗺️ Roadmap

- [ ] WebSocket support for real-time streaming
- [ ] Multi-user authentication system
- [ ] Prometheus metrics integration
- [ ] GraphQL API endpoint
- [ ] Browser extension
- [ ] Mobile SDK (iOS/Android)
- [ ] Kubernetes Helm charts
- [ ] Advanced prompt templates

---

<p align="center">
  Made with ❤️ by <a href="https://github.com/falkensmz">falkensmz</a>
</p>
