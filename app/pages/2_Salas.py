import streamlit as st

from app.services.salas import listar_salas, nome_tipo_sala
from app.services.equipamentos import obter_equipamentos_da_sala
from app.utils.session import exigir_usuario_selecionado
from app.components.cards import card_sala

st.set_page_config(
    page_title="Salas - UNISAPIENS",
    page_icon="🏢",
    layout="wide"
)

usuario_atual = exigir_usuario_selecionado()

st.title("🏢 Salas e Laboratórios")
st.caption(f"Sessão: {usuario_atual['nome']}")

col1, col2, col3 = st.columns(3)

with col1:
    apenas_disponiveis = st.checkbox(
        "Somente disponíveis",
        value=False
    )

with col2:
    capacidade_minima = st.number_input(
        "Capacidade mínima",
        min_value=0,
        value=0,
        step=1
    )

with col3:
    df_todas = listar_salas()

    predios = (
        ["Todos"] + sorted(df_todas["predio"].unique().tolist())
        if not df_todas.empty
        else ["Todos"]
    )

    predio_selecionado = st.selectbox(
        "Prédio",
        options=predios
    )

df = listar_salas(
    apenas_disponiveis=apenas_disponiveis
)

if capacidade_minima > 0 and not df.empty:
    df = df[
        df["capacidade"].astype(int) >= capacidade_minima
    ]

if predio_selecionado != "Todos" and not df.empty:
    df = df[
        df["predio"] == predio_selecionado
    ]

st.divider()

if df.empty:
    st.info(
        "Nenhuma sala encontrada com os filtros selecionados."
    )
else:
    st.write(
        f"**{len(df)} sala(s) encontrada(s):**"
    )

    for _, sala in df.iterrows():
        equipamentos = obter_equipamentos_da_sala(sala["idSala"])
        tipo = nome_tipo_sala(sala["idTipoSala"])

        if card_sala(sala, tipo, equipamentos, texto_botao="Ver detalhes"):
            st.session_state["sala_selecionada_id"] = sala["idSala"]
            st.switch_page("app/pages/3_Detalhes_Sala.py")