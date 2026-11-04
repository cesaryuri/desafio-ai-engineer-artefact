import os
import streamlit as st
from dotenv import load_dotenv
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
from langchain_core.runnables import RunnableConfig

from db.database import get_db
from rag.vectorstore import initialize_rag_system
from agent.llm import build_llm
from agent.tools import make_tools
from agent.graph import build_graph
from prompts.system_prompt import build_system_prompt
from ui.styles import apply_custom_styles
from ui.components import (
    ASSISTANT_AVATAR_SVG,
    TOOL_META,
    render_empty_state,
    render_sidebar,
    render_tool_tag,
    render_user_message,
)

load_dotenv()

st.set_page_config(
    page_title="Empório da Música — Assistente Virtual",
    page_icon="♪",
    layout="centered",
)
apply_custom_styles()

DB_URL = os.getenv("DATABASE_URL")
DB_ALLOWED_TABLES = os.getenv("DB_ALLOWED_TABLES", "")
ALLOWED = [t.strip() for t in DB_ALLOWED_TABLES.split(",") if t.strip()] or None
MAX_STEPS = int(os.getenv("MAX_AGENT_STEPS", "10"))


@st.cache_resource(show_spinner=True)
def load_resources():
    db = get_db(db_url=DB_URL)
    vectorstore = initialize_rag_system()
    return db, vectorstore


db, vectorstore = load_resources()

schema_info = ""
if db:
    try:
        schema_info = db.get_table_info(table_names=ALLOWED)
    except Exception as e:
        st.error(f"Erro ao ler esquema do banco: {e}")

SYSTEM_PROMPT = build_system_prompt(schema_info=schema_info, max_steps=MAX_STEPS)

tools = make_tools(db, vectorstore)
llm, DEFAULT_MODEL = build_llm(tools)
app = build_graph(llm, tools, max_tool_turns=MAX_STEPS)

if "messages" not in st.session_state:
    st.session_state["messages"] = [SystemMessage(SYSTEM_PROMPT)]


def reset_conversation() -> None:
    st.session_state["messages"] = [SystemMessage(SYSTEM_PROMPT)]


render_sidebar(model_name=DEFAULT_MODEL, on_reset_callback=reset_conversation)

has_user_messages = any(isinstance(m, HumanMessage) for m in st.session_state["messages"])
quick_prompt = None

if not has_user_messages:
    quick_prompt = render_empty_state()
else:
    for msg in st.session_state["messages"]:
        if isinstance(msg, HumanMessage):
            render_user_message(msg.content)
        elif isinstance(msg, ToolMessage):
            tool_name = msg.name or "tool"
            meta = TOOL_META.get(tool_name, {"expander": f"Ver retorno da ferramenta ({tool_name})"})
            render_tool_tag(tool_name)
            with st.expander(meta["expander"]):
                st.code(msg.content, language="json")
        elif isinstance(msg, AIMessage) and not msg.tool_calls:
            texto = getattr(msg, "text", None) or msg.content
            if texto:
                with st.chat_message("assistant", avatar=ASSISTANT_AVATAR_SVG):
                    st.markdown(texto)

chat_prompt = st.chat_input("Pergunte sobre instrumentos, pedidos ou políticas da loja…")

active_prompt = quick_prompt or chat_prompt

if active_prompt:
    st.session_state["messages"].append(HumanMessage(active_prompt))
    if has_user_messages:
        render_user_message(active_prompt)

    with st.chat_message("assistant", avatar=ASSISTANT_AVATAR_SVG):
        with st.status("Processando sua solicitação...", expanded=True) as status:
            novas_msgs = []
            for event in app.stream(
                {"messages": st.session_state["messages"]},
                config=RunnableConfig(recursion_limit=MAX_STEPS * 2 + 2),
            ):
                for node_name, node_state in event.items():
                    if node_name == "agent":
                        for msg in node_state["messages"]:
                            if isinstance(msg, AIMessage) and msg.tool_calls:
                                first_tool = msg.tool_calls[0].get("name", "")
                                meta = TOOL_META.get(first_tool)
                                if meta:
                                    status.update(label=meta["running_title"], state="running")
                                    st.caption(meta["running_sub"])
                    elif node_name == "tools":
                        for msg in node_state["messages"]:
                            if isinstance(msg, ToolMessage):
                                tool_name = msg.name or "tool"
                                meta = TOOL_META.get(
                                    tool_name,
                                    {"expander": f"Ver retorno da ferramenta ({tool_name})"},
                                )
                                render_tool_tag(tool_name)
                                with st.expander(meta["expander"]):
                                    st.code(msg.content, language="json")
                    novas_msgs.extend(node_state["messages"])

            status.update(label="Consulta concluída!", state="complete", expanded=False)

        st.session_state["messages"].extend(novas_msgs)

        resposta_final = ""
        for m in reversed(novas_msgs):
            if isinstance(m, AIMessage) and not m.tool_calls:
                resposta_final = getattr(m, "text", None) or m.content
                break

        if resposta_final:
            st.markdown(resposta_final)

    if quick_prompt:
        st.rerun()
