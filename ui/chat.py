import html
import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langchain_core.runnables import RunnableConfig

ASSISTANT_AVATAR_SVG = (
    "data:image/svg+xml;utf8,"
    "<svg xmlns='http://www.w3.org/2000/svg' width='36' height='36' viewBox='0 0 36 36'>"
    "<circle cx='18' cy='18' r='18' fill='%23d9a441'/>"
    "<text x='18' y='24' text-anchor='middle' font-family='sans-serif' "
    "font-size='18' font-weight='bold' fill='%231a1305'>♪</text>"
    "</svg>"
)

TOOL_META = {
    "query_sql": {
        "running_title": "Consultando estoque e pedidos",
        "running_sub": "Executando query_sql no catálogo SQLite…",
        "done_tag": "Consultou o catálogo · query_sql",
        "expander": "Ver retorno da ferramenta (query_sql)",
    },
    "search_store_policies": {
        "running_title": "Consultando políticas da loja",
        "running_sub": "Buscando trechos relevantes em politicas_loja.pdf…",
        "done_tag": "Consultou as políticas da loja · search_store_policies",
        "expander": "Ver retorno da ferramenta (search_store_policies)",
    },
}


def render_user_message(content: str) -> None:
    escaped = html.escape(content).replace("\n", "<br>")
    st.markdown(
        f"""
        <div class="em-user-row">
            <div class="em-user-bubble">{escaped}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_tool_tag(tool_name: str) -> None:
    meta = TOOL_META.get(tool_name, {"done_tag": f"Executou ferramenta · {tool_name}"})
    st.markdown(
        f"""
        <div class="em-tool-tag">
            <span class="em-tool-check">✓</span>
            <span>{html.escape(meta['done_tag'])}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


# Renderiza o histórico de mensagens, tags de ferramentas e respostas anteriores
def render_chat_history(messages: list) -> None:
    for msg in messages:
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


# Lê a barra de chat e transcreve automaticamente caso o cliente envie áudio
def get_chat_input(transcribe_fn) -> str | None:
    submission = st.chat_input(
        "Pergunte sobre instrumentos, pedidos ou políticas da loja…",
        accept_audio=True,
    )
    if not submission:
        return None

    if isinstance(submission, str):
        return submission
    if getattr(submission, "text", None):
        return submission.text
    if getattr(submission, "audio", None):
        with st.spinner("🎙️ Transcrevendo áudio..."):
            return transcribe_fn(submission.audio)
    return None


# Executa o grafo LangGraph exibindo o progresso das ferramentas em tempo real
def run_assistant_turn(app, messages: list, max_steps: int) -> list:
    novas_msgs = []

    with st.chat_message("assistant", avatar=ASSISTANT_AVATAR_SVG):
        with st.status("Processando sua solicitação...", expanded=True) as status:
            for event in app.stream(
                {"messages": messages},
                config=RunnableConfig(recursion_limit=max_steps * 2 + 2),
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

        resposta_final = ""
        for m in reversed(novas_msgs):
            if isinstance(m, AIMessage) and not m.tool_calls:
                resposta_final = getattr(m, "text", None) or m.content
                break

        if resposta_final:
            st.markdown(resposta_final)

    return novas_msgs
