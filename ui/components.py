from datetime import datetime
import html
import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage

ASSISTANT_AVATAR_SVG = (
    "data:image/svg+xml;utf8,"
    "<svg xmlns='http://www.w3.org/2000/svg' width='36' height='36' viewBox='0 0 36 36'>"
    "<circle cx='18' cy='18' r='18' fill='%23d9a441'/>"
    "<text x='18' y='24' text-anchor='middle' font-family='sans-serif' "
    "font-size='18' font-weight='bold' fill='%231a1305'>♪</text>"
    "</svg>"
)

QUICK_ACTIONS = [
    ("🎸 Violões até R$ 1.000", "Quais opções de violões disponíveis custando até R$ 1.000?"),
    ("🏷️ Promoções e Desconto no PIX", "Quais instrumentos estão em promoção e como funciona o desconto no PIX?"),
    ("📦 Consultar / Devolver Pedido", "Me arrependi da minha compra, posso devolver meu pedido?"),
    ("📍 Endereço e Horários", "Qual o endereço e o horário de funcionamento da loja?"),
    ("👤 Falar com Atendente", "Quero falar com um atendente humano"),
]

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


def export_chat_markdown(messages: list) -> str:
    lines = [
        "# Empório da Música — Histórico de Conversa",
        f"_Exportado em {datetime.now().strftime('%d/%m/%Y %H:%M')}_",
        "",
    ]
    for msg in messages:
        if isinstance(msg, HumanMessage):
            lines.append(f"### 👤 Cliente\n{msg.content}\n")
        elif isinstance(msg, AIMessage) and msg.content:
            lines.append(f"### ♪ Assistente Empório da Música\n{msg.content}\n")
    return "\n".join(lines)


def render_sidebar(model_name: str, on_reset_callback) -> None:
    with st.sidebar:
        st.markdown(
            """
            <div class="em-brand">
                <div class="em-logo-circle">♪</div>
                <div>
                    <div class="em-brand-title">Empório da Música</div>
                    <div class="em-brand-sub">Campo Grande · MS</div>
                </div>
            </div>
            <div class="em-divider"></div>
            <div class="em-atendimento-card">
                <div class="em-card-label">Atendimento</div>
                <div class="em-card-line">Seg–Sex &nbsp;9h às 18h</div>
                <div class="em-card-line">Sáb &nbsp;9h às 13h</div>
                <div class="em-card-muted">WhatsApp humano</div>
                <div class="em-card-phone">(67) 3341-4444</div>
            </div>
            <div class="em-divider"></div>
            <div class="em-section-title">Status do Sistema</div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
            <div class="em-status-row">
                <span class="em-status-left"><span class="em-dot"></span>Modelo LLM</span>
                <span class="em-status-val">{html.escape(model_name)}</span>
            </div>
            <div class="em-status-row">
                <span class="em-status-left"><span class="em-dot"></span>SQLite</span>
                <span class="em-status-val">conectado</span>
            </div>
            <div class="em-status-row">
                <span class="em-status-left"><span class="em-dot"></span>Base RAG (FAISS)</span>
                <span class="em-status-val">ativa</span>
            </div>
            <div class="em-divider"></div>
            """,
            unsafe_allow_html=True,
        )

        if st.button("🗑️  Nova conversa", use_container_width=True):
            on_reset_callback()
            st.rerun()

        chat_md = export_chat_markdown(st.session_state.get("messages", []))
        st.download_button(
            label="📥  Exportar conversa (.md)",
            data=chat_md.encode("utf-8"),
            file_name="conversa_emporio_da_musica.md",
            mime="text/markdown",
            use_container_width=True,
        )


def render_empty_state() -> str | None:
    st.markdown(
        """
        <div class="em-hero">
            <div class="em-badge">Assistente Virtual</div>
            <h1 class="em-hero-title">Empório da Música</h1>
            <p class="em-hero-sub">Instrumentos musicais em Campo Grande/MS</p>
        </div>

        <div class="em-welcome-card">
            <div class="em-avatar-sm">♪</div>
            <div>
                <div class="em-welcome-title">Olá! Sou o assistente da Empório da Música.</div>
                <div class="em-welcome-body">
                    Consulto estoque, preços e promoções, e respondo dúvidas sobre frete,
                    trocas, devoluções e garantia. Por onde quer começar?
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    selected_prompt = None

    row1 = st.columns(3)
    for col, (label, prompt_text) in zip(row1, QUICK_ACTIONS[:3]):
        with col:
            if st.button(label, key=f"qa_{label}", use_container_width=True):
                selected_prompt = prompt_text

    row2 = st.columns([1.2, 1.2, 0.6])
    for col, (label, prompt_text) in zip(row2[:2], QUICK_ACTIONS[3:]):
        with col:
            if st.button(label, key=f"qa_{label}", use_container_width=True):
                selected_prompt = prompt_text

    return selected_prompt


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
    meta = TOOL_META.get(
        tool_name,
        {
            "done_tag": f"Executou ferramenta · {tool_name}",
        },
    )
    st.markdown(
        f"""
        <div class="em-tool-tag">
            <span class="em-tool-check">✓</span>
            <span>{html.escape(meta['done_tag'])}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
