# LLM Gateway

A unified FastAPI gateway that routes chat completions through multiple LLM providers behind a single API.

## Supported Providers

| Provider  | Backend         | Config Key           |
|-----------|-----------------|----------------------|
| OpenAI    | OpenAI Cloud    | `OPENAI_API_KEY`     |
| Anthropic | Anthropic Cloud | `ANTHROPIC_API_KEY`  |
| Gemini    | Google GenAI    | `GEMINI_API_KEY`     |
| Ollama    | Local models    | `OLLAMA_HOST`        |

## Architecture

```
               FastAPI
                  │
              LLMService
                  │
            LLMProvider (base)
           ┌──────┼──────────┐──────────┐
           │      │          │          │
        OpenAI  Anthropic  Gemini    Ollama
           │      │          │          │
        Cloud   Cloud      Cloud    Local Model
```

## Project Structure

```
app/
├── main.py
├── config/
│   ├── config.py
│   ├── schemas.py
│   ├── dependencies.py
│   └── retry.py
├── providers/
│   ├── base.py
│   ├── openai_provider.py
│   ├── anthropic_provider.py
│   ├── gemini_provider.py
│   ├── ollama_provider.py
│   └── registry.py
├── routes/
│   ├── chat.py
│   └── health.py
├── services/
│   └── llm_service.py
└── exceptions/
    ├── exception.py
    └── error_handler.py
tests/
├── fakes.py
├── test_successretries.py
├── test_permanenterrors.py
└── test_stopbudget.py
```

## Getting Started

### Prerequisites

- Python 3.11+
- [Ollama](https://ollama.com) (for local models)

### Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Configuration

Copy the example env file and fill in your API keys:

```bash
cp .env.example .env
```

| Variable                  | Default                   | Description               |
|---------------------------|---------------------------|---------------------------|
| `DEFAULT_PROVIDER`        | `ollama`                  | Provider used when none specified |
| `OPENAI_API_KEY`          | —                         | OpenAI API key            |
| `OPENAI_MODEL`            | `gpt-5.6-luna`            | Default OpenAI model      |
| `ANTHROPIC_API_KEY`       | —                         | Anthropic API key         |
| `ANTHROPIC_MODEL`         | `claude-sonnet-4-5`       | Default Anthropic model   |
| `GEMINI_API_KEY`          | —                         | Google Gemini API key     |
| `GEMINI_MODEL`            | `gemini-3.8-flash`        | Default Gemini model      |
| `OLLAMA_HOST`             | `http://localhost:11434`  | Ollama server URL         |
| `OLLAMA_MODEL`            | `gemma4`                  | Default Ollama model      |
| `MAX_OUTPUT_TOKENS`       | `1024`                    | Max tokens per response   |
| `LLM_TIMEOUT_SECONDS`    | `30`                      | Request timeout           |
| `LLM_MAX_ATTEMPTS`       | `3`                       | Retry attempts on failure |
| `LLM_RETRY_INITIAL_DELAY`| `0.5`                     | Initial retry delay (sec) |
| `LLM_RETRY_MAX_DELAY`    | `8`                       | Max retry delay (sec)     |

### Run

```bash
# Start Ollama (if using local models)
ollama run gemma4

# Start the gateway
uvicorn app.main:app --reload
```

API docs available at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

### Tests

```bash
pytest
```
