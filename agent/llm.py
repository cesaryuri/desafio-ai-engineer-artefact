import os
from openai import OpenAI
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_anthropic import ChatAnthropic

# Modelos Claude "5" que não aceitam o parâmetro temperature
MODELOS_SEM_TEMPERATURA = {"claude-sonnet-5", "claude-opus-5", "claude-fable-5"}


def get_embeddings():
    provider = os.getenv("EMBEDDING_PROVIDER") or os.getenv("LLM_PROVIDER", "openai")
    model = os.getenv("EMBEDDING_MODEL")

    if provider == "ollama":
        return OllamaEmbeddings(model=model or "embeddinggemma:latest")

    if provider == "openai":
        return OpenAIEmbeddings(model=model or "text-embedding-3-small")

    return GoogleGenerativeAIEmbeddings(model=model or "models/gemini-embedding-001")


def build_llm(tools: list):
    provider = os.getenv("LLM_PROVIDER", "openai")
    model = os.getenv("LLM_MODEL", "gpt-5.4-mini")

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


def transcribe_audio(audio_file) -> str:
    client = OpenAI()
    model = os.getenv("OPENAI_STT_MODEL", "gpt-4o-mini-transcribe")
    transcription = client.audio.transcriptions.create(
        model=model,
        file=audio_file,
        language="pt",
    )
    return transcription.text.strip()
