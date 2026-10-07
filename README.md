llm-gateway/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── schemas.py
│   │
│   ├── providers/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── openai_provider.py
│   │   └── ollama_provider.py
│   │
│   └── services/
│       ├── __init__.py
│       └── llm_service.py
│
├── tests/
│
├── .env
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md

Architecture


                 FastAPI
                    ↓
                LLMService
                    ↓
                LLMProvider
                 /       \
                /         \
               ↓           ↓
        OpenAIProvider   OllamaProvider
               ↓           ↓
        OpenAI Cloud     Local Model



<!-- GUIDE -->

python -m venv .venv

source .venv/bin/activate

pip install -r requirements.txt

ollama run gemma4

to start app - uvicorn app.main:app --reload

docs avialbale at http://127.0.0.1:8000/docs



python -m pip install pytest pytest-asyncio


<!-- https://arxiv.org/pdf/2502.11208 -->