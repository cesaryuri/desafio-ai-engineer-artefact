import streamlit as st

FIGMA_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Playfair+Display:wght@700&family=Roboto+Mono:wght@400;500&display=swap');

:root {
    --bg-main: #121110;
    --bg-sidebar: #1a1816;
    --bg-card: #211e1b;
    --bg-chip: #27231f;
    --bg-user-bubble: #2b2620;
    --bg-code: #161412;
    --border-color: #34302b;
    --gold: #d9a441;
    --gold-surface: #2a2112;
    --gold-dark-text: #1a1305;
    --green: #6bbf8a;
    --text-primary: #f3eee6;
    --text-muted: #a0968a;
}

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    color: var(--text-primary);
}

.stApp {
    background-color: var(--bg-main);
}

/* Centraliza container principal no limite de 760px do Figma */
.block-container {
    max-width: 820px !important;
    padding-top: 2.5rem !important;
    padding-bottom: 4rem !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: var(--bg-sidebar) !important;
    border-right: 1px solid var(--border-color);
}

[data-testid="stSidebar"] .block-container {
    padding-top: 1.5rem !important;
    padding-left: 1.25rem !important;
    padding-right: 1.25rem !important;
}

.em-brand {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 20px;
}

.em-logo-circle {
    width: 44px;
    height: 44px;
    border-radius: 50%;
    background-color: var(--gold);
    color: var(--gold-dark-text);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 20px;
    font-weight: 700;
    flex-shrink: 0;
}

.em-brand-title {
    font-family: 'Playfair Display', serif;
    font-weight: 700;
    font-size: 18px;
    color: var(--text-primary);
    line-height: 1.2;
}

.em-brand-sub {
    font-size: 12px;
    color: var(--text-muted);
    margin-top: 2px;
}

.em-divider {
    height: 1px;
    background-color: var(--border-color);
    margin: 18px 0;
}

.em-atendimento-card {
    background-color: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    padding: 16px;
}

.em-card-label {
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.9px;
    color: var(--gold);
    text-transform: uppercase;
    margin-bottom: 8px;
}

.em-card-line {
    font-size: 13px;
    color: var(--text-primary);
    line-height: 1.5;
}

.em-card-muted {
    font-size: 12px;
    color: var(--text-muted);
    margin-top: 8px;
}

.em-card-phone {
    font-size: 15px;
    font-weight: 600;
    color: var(--gold);
    margin-top: 2px;
}

.em-section-title {
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.9px;
    color: var(--text-muted);
    text-transform: uppercase;
    margin-bottom: 10px;
}

.em-status-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    font-size: 12.5px;
    margin-bottom: 8px;
}

.em-status-left {
    display: flex;
    align-items: center;
    gap: 8px;
    color: var(--text-muted);
}

.em-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background-color: var(--green);
    display: inline-block;
}

.em-status-val {
    color: var(--text-primary);
    font-weight: 500;
}

/* Botões da Sidebar */
[data-testid="stSidebar"] .stButton > button {
    background-color: transparent;
    border: 1px solid var(--border-color);
    color: var(--text-primary);
    border-radius: 10px;
    font-size: 13px;
    font-weight: 500;
    padding: 0.55rem 0.75rem;
}

[data-testid="stSidebar"] .stButton > button:hover {
    border-color: var(--gold);
    color: var(--gold);
}

[data-testid="stSidebar"] .stDownloadButton > button {
    background-color: transparent;
    border: 1px solid var(--gold);
    color: var(--gold);
    border-radius: 10px;
    font-size: 13px;
    font-weight: 500;
    padding: 0.55rem 0.75rem;
}

[data-testid="stSidebar"] .stDownloadButton > button:hover {
    background-color: var(--gold-surface);
}

/* Hero — Estado Inicial */
.em-hero {
    text-align: center;
    margin-top: 1.5rem;
    margin-bottom: 2rem;
}

.em-badge {
    display: inline-block;
    background-color: var(--gold-surface);
    border: 1px solid var(--gold);
    color: var(--gold);
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 1px;
    text-transform: uppercase;
    padding: 4px 12px;
    border-radius: 999px;
    margin-bottom: 14px;
}

.em-hero-title {
    font-family: 'Playfair Display', serif;
    font-weight: 700;
    font-size: 44px;
    color: var(--text-primary);
    margin: 0 0 8px 0;
    line-height: 1.15;
}

.em-hero-sub {
    font-size: 16px;
    color: var(--text-muted);
    margin: 0;
}

/* Card de Boas-vindas */
.em-welcome-card {
    background-color: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: 16px;
    padding: 20px;
    display: flex;
    align-items: flex-start;
    gap: 14px;
    margin-bottom: 20px;
}

.em-avatar-sm {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    background-color: var(--gold);
    color: var(--gold-dark-text);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 16px;
    font-weight: 700;
    flex-shrink: 0;
}

.em-welcome-title {
    font-size: 15px;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 6px;
}

.em-welcome-body {
    font-size: 14.5px;
    color: var(--text-muted);
    line-height: 1.55;
}

/* Chips de ação rápida na área principal */
.stMain .stButton > button {
    background-color: var(--bg-card);
    border: 1px solid var(--border-color);
    color: var(--text-primary);
    border-radius: 999px;
    font-size: 13px;
    font-weight: 500;
    padding: 0.45rem 1rem;
    transition: all 0.15s ease;
}

.stMain .stButton > button:hover {
    border-color: var(--gold);
    color: var(--gold);
    background-color: var(--gold-surface);
}

/* Balão de mensagem do usuário alinhado à direita (Frame 1:72) */
.em-user-row {
    display: flex;
    justify-content: flex-end;
    margin: 1rem 0;
}

.em-user-bubble {
    background-color: var(--bg-user-bubble);
    border: 1px solid var(--border-color);
    color: var(--text-primary);
    border-radius: 16px;
    padding: 12px 16px;
    max-width: 75%;
    font-size: 15px;
    line-height: 1.5;
}

/* Mensagem do assistente com avatar dourado ♪ */
.em-assistant-row {
    display: flex;
    align-items: flex-start;
    gap: 12px;
    margin: 1rem 0;
}

.em-avatar-chat {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    background-color: var(--gold);
    color: var(--gold-dark-text);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 14px;
    font-weight: 700;
    flex-shrink: 0;
    margin-top: 2px;
}

/* Tag monospace de ferramenta executada (Frame 6:2) */
.em-tool-tag {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background-color: var(--bg-chip);
    border: 1px solid var(--border-color);
    border-radius: 8px;
    padding: 5px 10px;
    font-family: 'Roboto Mono', monospace;
    font-size: 12px;
    color: var(--text-muted);
    margin-bottom: 6px;
}

.em-tool-check {
    color: var(--green);
    font-weight: 700;
}

/* Status e Expanders */
[data-testid="stStatusWidget"], [data-testid="stExpander"] {
    background-color: var(--bg-card) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 12px !important;
}

/* Rodapé abaixo do chat input */
.em-footer-note {
    text-align: center;
    font-size: 11.5px;
    color: var(--text-muted);
    margin-top: 8px;
}
</style>
"""


def apply_custom_styles() -> None:
    st.markdown(FIGMA_CSS, unsafe_allow_html=True)
