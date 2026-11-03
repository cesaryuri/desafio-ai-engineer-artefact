import os
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_anthropic import ChatAnthropic

DEFAULT_MODEL = os.getenv("LLM_MODEL", "gpt-5.4-mini")  # gemini-3.8-flash | gpt-5.4-mini | claude-haiku-4-5-20251001 | claude-sonnet-5
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")  # google | openai | anthropic | ollama

    #   Google:
    #   gemini-3.8-flash

    #   OpenAI:
    #   gpt-5.4-mini
    #   gpt-5-mini
    #   gpt-5.2
    #   gpt-4o

    #   Ollama (Local):
    #   gemma3:4b
    #   gemma3:12b
    #   llama3.2:3b
    #   llama3.2:latest

    #   Anthropic:
    #   claude-haiku-4-5-20251001 (modelo econômico)
    #   claude-sonnet-4-6
    #   claude-sonnet-5
    #   claude-opus-5

# Modelos Claude "5" (sonnet-5, opus-5, fable-5) não aceitam o parâmetro temperature
MODELOS_SEM_TEMPERATURA = {"claude-sonnet-5", "claude-opus-5", "claude-fable-5"}


def get_embeddings():
    provider = os.getenv("EMBEDDING_PROVIDER") or os.getenv("LLM_PROVIDER", LLM_PROVIDER)

    if provider == "ollama":
        model = os.getenv("EMBEDDING_MODEL", "embeddinggemma:latest")
        return OllamaEmbeddings(model=model)

    if provider == "openai":
        model = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
        return OpenAIEmbeddings(model=model)

    model = os.getenv("EMBEDDING_MODEL", "models/gemini-embedding-001")
    return GoogleGenerativeAIEmbeddings(model=model)


def build_llm(tools: list):
    provider = os.getenv("LLM_PROVIDER", LLM_PROVIDER)
    model = os.getenv("LLM_MODEL", DEFAULT_MODEL)

    if provider == "google":
        llm = ChatGoogleGenerativeAI(model=model, temperature=0.2)

    elif provider == "openai":
        llm = ChatOpenAI(model=model, temperature=0.2)

    elif provider == "ollama":
        llm = ChatOllama(model=model, temperature=0.2)

    elif provider == "anthropic":
        kwargs = {"model": model}
        if model not in MODELOS_SEM_TEMPERATURA:
            kwargs["temperature"] = 0.2
        llm = ChatAnthropic(**kwargs)

    else:
        raise ValueError(f"LLM_PROVIDER desconhecido: {provider!r}")

    return llm.bind_tools(tools), model
