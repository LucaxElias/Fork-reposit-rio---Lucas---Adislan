"""
Utilitário para simular o usuário logado (N1 - sem autenticação real).
Usa st.session_state para "fixar" o usuário durante toda a navegação
entre as páginas do Streamlit.
"""

import streamlit as st

CHAVE_USUARIO_ATUAL = "usuario_atual"


def definir_usuario_atual(usuario: dict) -> None:
    """Fixa o usuário selecionado na sessão."""
    st.session_state[CHAVE_USUARIO_ATUAL] = usuario


def obter_usuario_atual():
    """Retorna o dict do usuário fixado na sessão, ou None se nenhum foi selecionado."""
    return st.session_state.get(CHAVE_USUARIO_ATUAL)


def usuario_selecionado() -> bool:
    """Verifica se já existe um usuário fixado na sessão."""
    return obter_usuario_atual() is not None


def exigir_usuario_selecionado() -> dict:
    """
    Usada no início de páginas que exigem usuário fixado.
    Interrompe a renderização da página com uma mensagem clara caso
    nenhum usuário tenha sido selecionado ainda.
    """
    usuario = obter_usuario_atual()
    if usuario is None:
        st.warning("Selecione um usuário na página inicial (Home) antes de continuar.")
        st.stop()
    return usuario