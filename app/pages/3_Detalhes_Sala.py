import streamlit as st

from app.services.salas import buscar_sala_por_id, listar_salas
from app.services.reservas import listar_reservas_por_sala
from app.utils.session import exigir_usuario_selecionado

st.set_page_config(
    page_title="Detalhes da Sala - UNISAPIENS",
    page_icon="🔍",
    layout="wide"
)

usuario_atual = exigir_usuario_selecionado()

st.title("🔍 Detalhes da Sala")

sala_id_padrao = st.session_state.get(
    "sala_selecionada_id"
)

df_salas = listar_salas()

if df_salas.empty:
    st.error("Nenhuma sala cadastrada.")
    st.stop()

opcoes_ids = df_salas["idSala"].tolist()

indice_padrao = (
    opcoes_ids.index(sala_id_padrao)
    if sala_id_padrao in opcoes_ids
    else 0
)

sala_id = st.selectbox(
    "Sala",
    options=opcoes_ids,
    index=indice_padrao,
    format_func=lambda i: df_salas[
        df_salas["idSala"] == i
    ]["nome"].values[0],
)

sala = buscar_sala_por_id(sala_id)

if sala is None:
    st.error("Sala não encontrada.")
    st.stop()

st.session_state["sala_selecionada_id"] = sala_id

st.divider()

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader(sala["nome"])

    st.write(
        f"📍 **Localização:** "
        f"{sala['predio']} - "
        f"{sala['andar']}º andar"
    )

    st.write(
        f"👥 **Capacidade:** "
        f"{sala['capacidade']} pessoas"
    )

    if sala.get("descricao"):
        st.write(
            f"📝 **Descrição:** "
            f"{sala['descricao']}"
        )

with col2:
    cor = {
        "Disponivel": "🟢",
        "Manutencao": "🟠",
        "Indisponivel": "🔴"
    }.get(
        sala["status"],
        "⚪"
    )

    st.metric(
        "Status atual",
        f"{cor} {sala['status']}"
    )

    if sala["status"] == "Disponivel":

        if st.button(
            "📅 Reservar esta sala",
            type="primary"
        ):
            st.session_state[
                "sala_reservar_id"
            ] = sala_id

            st.switch_page(
                "app/pages/4_Reservar.py"
            )

    else:
        st.button(
            "📅 Reservar esta sala",
            disabled=True,
            help="Sala indisponível para reserva"
        )

st.divider()

st.subheader("📋 Reservas confirmadas")

df_reservas = listar_reservas_por_sala(
    sala_id,
    apenas_confirmadas=True
)

if df_reservas.empty:
    st.info(
        "Nenhuma reserva confirmada para esta sala."
    )
else:
    df_exibicao = df_reservas[
        ["data", "horaInicio", "horaFim", "idUser"]
    ].copy()

    df_exibicao.columns = [
        "Data",
        "Início",
        "Fim",
        "ID Usuário"
    ]

    st.dataframe(
        df_exibicao,
        use_container_width=True,
        hide_index=True
    )