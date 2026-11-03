import os
import streamlit as st
from dotenv import load_dotenv
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
from langchain_core.runnables import RunnableConfig

from db.database import get_db
from rag.vectorstore import initialize_rag_system
from agent.llm import build_llm, get_embeddings
from agent.tools import make_tools
from agent.graph import build_graph
from prompts.system_prompt import build_system_prompt

load_dotenv()

st.set_page_config(page_title="Atendimento — Empório da Música", layout="centered")
st.title("🎸 Empório da Música — Assistente Virtual")

DB_URL = os.getenv("DATABASE_URL")
MAX_STEPS = int(os.getenv("MAX_AGENT_STEPS", "10"))


@st.cache_resource(show_spinner=True)
def load_resources():
    db = get_db(db_url=DB_URL)
    embeddings = get_embeddings()
    vectorstore = initialize_rag_system(embeddings=embeddings)
    return db, vectorstore


db, vectorstore = load_resources()

schema_info = ""
if db:
    try:
        schema_info = db.get_table_info()
    except Exception as e:
        st.error(f"Erro ao ler esquema do banco: {e}")

SYSTEM_PROMPT = build_system_prompt(schema_info=schema_info, max_steps=MAX_STEPS)

tools = make_tools(db, vectorstore)
llm, DEFAULT_MODEL = build_llm(tools)
app = build_graph(llm, tools, max_tool_turns=MAX_STEPS)

with st.sidebar:
    st.caption(f"Modelo ativo: `{DEFAULT_MODEL}`")
    if st.button("🗑️ Limpar conversa", use_container_width=True):
        st.session_state["messages"] = [SystemMessage(SYSTEM_PROMPT)]
        st.rerun()

if "messages" not in st.session_state:
    st.session_state["messages"] = [SystemMessage(SYSTEM_PROMPT)]

for msg in st.session_state["messages"]:
    if isinstance(msg, HumanMessage):
        with st.chat_message("user"):
            st.markdown(msg.content)
    elif isinstance(msg, AIMessage) and not msg.tool_calls:
        texto = getattr(msg, "text", None) or msg.content
        if texto:
            with st.chat_message("assistant"):
                st.markdown(texto)

if user_input := st.chat_input("Digite sua dúvida sobre instrumentos, pedidos ou políticas da loja..."):
    st.session_state["messages"].append(HumanMessage(user_input))
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.status("Processando sua solicitação...", expanded=True) as status:
            novas_msgs = []
            for event in app.stream(
                {"messages": st.session_state["messages"]},
                config=RunnableConfig(recursion_limit=MAX_STEPS * 2 + 2),
            ):
                for node_name, node_state in event.items():
                    if node_name == "agent":
                        st.write("🧠 Analisando contexto...")
                    elif node_name == "tools":
                        st.write("🔍 Consultando base de dados / políticas...")
                        for msg in node_state["messages"]:
                            if isinstance(msg, ToolMessage):
                                with st.expander(f"Ver retorno da ferramenta ({msg.name or 'tool'})"):
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
