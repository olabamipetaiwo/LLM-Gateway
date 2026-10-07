### Ollama

  {
    "messages": [
      {"role": "system", "content": "You are a concise computer science tutor."},
      {"role": "user", "content": "Explain embeddings in three sentences."}
    ],
    "provider": "ollama"
  }

### OpenAI

  {
    "messages": [
      {"role": "system", "content": "You are a concise computer science tutor."},
      {"role": "user", "content": "Explain embeddings in three sentences."}
    ],
    "provider": "openai"
  }

### Anthropic

  {
    "messages": [
      {"role": "system", "content": "You are a concise computer science tutor."},
      {"role": "user", "content": "Explain embeddings in three sentences."}
    ],
    "provider": "anthropic"
  }

### Gemini

  {
    "messages": [
      {"role": "system", "content": "You are a concise computer science tutor."},
      {"role": "user", "content": "Explain embeddings in three sentences."}
    ],
    "provider": "gemini"
  }


  ## error

  {
  "messages": [
    {
      "role": "user",
      "content": "Hello"
    }
  ],
  "provider": "ollama",
  "model": "definitely-does-not-exist"
}