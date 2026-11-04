import streamlit as st
from dotenv import load_dotenv
from langchain_core.messages import SystemMessage, HumanMessage

from agent.chatbot import create_chatbot
from agent.llm import transcribe_audio
from ui.styles import apply_custom_styles
from ui.sidebar import render_sidebar
from ui.welcome import render_empty_state
from ui.chat import (
    get_chat_input,
    render_chat_history,
    render_user_message,
    run_assistant_turn,
)

load_dotenv()

st.set_page_config(
    page_title="Empório da Música — Assistente Virtual",
    page_icon="♪",
    layout="centered",
)
apply_custom_styles()


# Inicializa o assistente (SQLite, FAISS, prompt e grafo LangGraph) uma única vez em cache
@st.cache_resource(show_spinner=True)
def init_chatbot():
    return create_chatbot()


app, SYSTEM_PROMPT, DEFAULT_MODEL, MAX_STEPS = init_chatbot()

if "messages" not in st.session_state:
    st.session_state["messages"] = [SystemMessage(SYSTEM_PROMPT)]


def reset_conversation() -> None:
    st.session_state["messages"] = [SystemMessage(SYSTEM_PROMPT)]


render_sidebar(model_name=DEFAULT_MODEL, on_reset_callback=reset_conversation)

# Exibe tela inicial de boas-vindas enquanto o cliente ainda não iniciou conversa
has_user_messages = any(isinstance(m, HumanMessage) for m in st.session_state["messages"])
quick_prompt = render_empty_state() if not has_user_messages else None

if has_user_messages:
    render_chat_history(st.session_state["messages"])

# Processa entrada por clique rápido, texto digitado ou áudio transcrito
chat_prompt = get_chat_input(transcribe_audio)
active_prompt = quick_prompt or chat_prompt

if active_prompt:
    st.session_state["messages"].append(HumanMessage(active_prompt))
    render_user_message(active_prompt)

    novas_msgs = run_assistant_turn(app, st.session_state["messages"], max_steps=MAX_STEPS)
    st.session_state["messages"].extend(novas_msgs)

    if not has_user_messages:
        st.rerun()
