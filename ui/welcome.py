import streamlit as st

QUICK_ACTIONS = [
    ("🎸 Violões até R$ 1.000", "Quais opções de violões disponíveis custando até R$ 1.000?"),
    ("🏷️ Promoções e Desconto no PIX", "Quais instrumentos estão em promoção e como funciona o desconto no PIX?"),
    ("📦 Consultar / Devolver Pedido", "Me arrependi da minha compra, posso devolver meu pedido?"),
    ("📍 Endereço e Horários", "Qual o endereço e o horário de funcionamento da loja?"),
    ("👤 Falar com Atendente", "Quero falar com um atendente humano"),
]


# Exibe o estado inicial (Hero + Boas-vindas + Atalhos) enquanto não há mensagens do cliente
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
