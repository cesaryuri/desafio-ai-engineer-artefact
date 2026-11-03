import os
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_anthropic import ChatAnthropic

DEFAULT_MODEL = os.getenv("LLM_MODEL", "gemini-3.8-flash")
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "google")

MODELOS_SEM_TEMPERATURA = {"claude-sonnet-5", "claude-opus-5", "claude-fable-5"}


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
