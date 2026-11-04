from datetime import datetime
import html
import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage


# Formata o histórico da sessão atual em Markdown para download
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
