# Gemini CLI Wrapper & API

A Python wrapper and REST API for Google's Gemini CLI tool, designed to manage the free tier limitations (1000 requests/hour) with intelligent rate limiting, caching, and queuing.

## Features

- **Rate Limiting**: Tracks requests per hour with SQLite database
- **Smart Caching**: Caches responses to avoid duplicate API calls
- **Retry Logic**: Automatic retries with exponential backoff
- **Async Processing**: Queue requests for background processing
- **REST API**: Full HTTP API with Flask server
- **Batch Processing**: Process multiple prompts efficiently
- **Usage Statistics**: Track and monitor API usage

## Installation

```bash
# Install Python dependencies
pip install -r requirements.txt

# Make scripts executable
chmod +x gemini_api.py gemini_server.py examples.py
```

## Quick Start

### 1. Command Line Usage

```bash
# Single prompt
./gemini_api.py "Explain Python in one sentence"

# Check usage stats
./gemini_api.py --stats

# Batch processing
echo -e "What is AI?\nExplain ML\nDefine NLP" > prompts.txt
./gemini_api.py --batch prompts.txt --output results.json

# JSON output
./gemini_api.py "Your prompt" --json
```

### 2. Python API

```python
from gemini_api import GeminiAPI

# Initialize
api = GeminiAPI()

# Simple prompt
result = api.prompt("Write a haiku")
if result["success"]:
    print(result["output"])

# Check usage
stats = api.get_usage()
print(f"Remaining: {stats['remaining_this_hour']}")

# Batch processing
prompts = ["Question 1", "Question 2", "Question 3"]
results = api.batch_prompts(prompts)
```

### 3. REST API Server

```bash
# Start server
./gemini_server.py --host 0.0.0.0 --port 5000

# In another terminal:
# Send prompt
curl -X POST http://localhost:5000/prompt \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Hello Gemini"}'

# Check usage
curl http://localhost:5000/usage

# Async request
curl -X POST http://localhost:5000/prompt/async \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Complex task"}'
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check and usage stats |
| `/usage` | GET | Current usage statistics |
| `/prompt` | POST | Send prompt (synchronous) |
| `/prompt/async` | POST | Queue prompt (asynchronous) |
| `/job/<id>` | GET | Check async job status |
| `/batch` | POST | Process multiple prompts |
| `/stream` | POST | Stream responses (SSE) |
| `/jobs` | GET | List all jobs |
| `/cache/clear` | POST | Clear response cache |

## Examples

Run examples:
```bash
# All examples
./examples.py

# Specific example
./examples.py basic   # Basic usage
./examples.py batch   # Batch processing
./examples.py async   # Async with callbacks
./examples.py rest    # REST API usage
./examples.py rate    # Rate limit handling
./examples.py cache   # Caching demonstration
```

## Configuration

### GeminiAPI Parameters

```python
api = GeminiAPI(
    auto_approve=True,        # Auto-approve tool calls (--yolo)
    checkpointing=True,       # Enable checkpointing
    max_retries=3,           # Retry failed requests
    rate_limit_per_hour=950  # Conservative limit (max 1000)
)
```

### Environment Variables

The wrapper respects the same environment variables as the Gemini CLI tool.

## Rate Limiting

The wrapper tracks API usage in `~/.gemini_rate_limit.db` and enforces a conservative limit of 950 requests/hour (below the 1000 limit). When the limit is reached:

1. Synchronous calls return an error with wait time
2. Async calls are queued automatically
3. Batch processing pauses until the limit resets

## Caching

Responses are cached in memory by default. Cache keys are generated from:
- Prompt text
- Extra flags

To bypass cache:
```python
result = api.prompt("Your prompt", use_cache=False)
```

## Error Handling

The wrapper handles:
- Rate limit errors (with wait time calculation)
- Timeout errors (5-minute default)
- Subprocess errors
- Network errors (in REST API)

All errors include detailed messages and usage statistics.

## Performance Tips

1. **Pre-batch prompts** when possible to optimize rate limit usage
2. **Use caching** for repeated queries
3. **Monitor usage** with `/usage` endpoint or `--stats` flag
4. **Adjust concurrency** based on your needs
5. **Use async** for non-blocking operations

## Troubleshooting

### Rate Limit Issues
- Check current usage: `./gemini_api.py --stats`
- Wait time is calculated automatically
- Database is at `~/.gemini_rate_limit.db`

### Server Issues
- Check server is running: `curl http://localhost:5000/health`
- Enable debug mode: `./gemini_server.py --debug`
- Check Flask logs for errors

### Gemini CLI Issues
- Ensure `gemini` CLI is installed and in PATH
- Test directly: `gemini --yolo -p "test"`
- Check authentication is configured

## License

This wrapper is provided as-is for use with Google's Gemini CLI tool.
