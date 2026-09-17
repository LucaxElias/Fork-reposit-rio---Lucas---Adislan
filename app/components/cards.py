"""
Componentes de UI reutilizáveis para exibir salas em formato de card.
"""

import streamlit as st

from app.utils.helpers import badge_status, tag_neutra, barra_status


def card_sala(sala, nome_tipo: str, equipamentos_df, texto_botao: str = "Ver detalhes") -> bool:
    """
    Renderiza um card de sala (barra de status, nome + badge, tipo,
    localização, capacidade, equipamentos, descrição e botão de ação).

    Retorna True se o botão de ação foi clicado nesta execução.
    """
    with st.container(border=True):
        st.markdown(barra_status(sala["status"]), unsafe_allow_html=True)

        col_nome, col_badge = st.columns([4, 1])

        with col_nome:
            st.markdown(f"### {sala['nome']}")

        with col_badge:
            st.markdown(badge_status(sala["status"]), unsafe_allow_html=True)

        st.markdown(tag_neutra(nome_tipo), unsafe_allow_html=True)

        st.write(f"📍 {sala['predio']} - {sala['andar']}º andar")
        st.write(f"👥 Capacidade: {sala['capacidade']} pessoas")

        if not equipamentos_df.empty:
            tags_html = "".join(
                tag_neutra(f"{linha['nome']} ({int(linha['quantidade'])})")
                for _, linha in equipamentos_df.iterrows()
            )
            st.markdown(tags_html, unsafe_allow_html=True)

        if sala.get("descricao"):
            st.caption(sala["descricao"])

        return st.button(texto_botao, key=f"card_sala_{sala['idSala']}_{texto_botao}")
