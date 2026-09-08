import streamlit as st

from app.services.salas import listar_salas
from app.utils.session import exigir_usuario_selecionado

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
        with st.container(border=True):

            col_info, col_status, col_acao = st.columns(
                [3, 1, 1]
            )

            with col_info:
                st.markdown(
                    f"### {sala['nome']}"
                )

                st.write(
                    f"📍 {sala['predio']} - "
                    f"{sala['andar']}º andar"
                )

                st.write(
                    f"👥 Capacidade: "
                    f"{sala['capacidade']} pessoas"
                )

                if sala.get("descricao"):
                    st.caption(
                        sala["descricao"]
                    )

            with col_status:
                cor = {
                    "Disponivel": "🟢",
                    "Manutencao": "🟠",
                    "Indisponivel": "🔴",
                }.get(
                    sala["status"],
                    "⚪"
                )

                st.metric(
                    "Status",
                    f"{cor} {sala['status']}"
                )

            with col_acao:
                st.write("")
                st.write("")

                if st.button(
                    "Ver detalhes",
                    key=f"ver_{sala['idSala']}"
                ):
                    st.session_state[
                        "sala_selecionada_id"
                    ] = sala["idSala"]

                    st.switch_page(
                        "app/pages/3_Detalhes_Sala.py"
                    )