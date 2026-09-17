import streamlit as st
from datetime import date, time

from app.services.salas import buscar_sala_por_id, listar_salas
from app.services.reservas import criar_reserva
from app.services.validacao import RegraNegocioError
from app.utils.session import exigir_usuario_selecionado


st.set_page_config(
    page_title="Reservar Sala - UNISAPIENS",
    page_icon="📅",
    layout="wide"
)

usuario_atual = exigir_usuario_selecionado()

st.title("📅 Reservar Sala")
st.caption(
    f"Reservando como: {usuario_atual['nome']} "
    f"(id {usuario_atual['idUser']}, {usuario_atual['role']})"
)

df_salas = listar_salas(apenas_disponiveis=True)

if df_salas.empty:
    st.warning("Não há salas disponíveis para reserva no momento.")
    st.stop()

sala_id_padrao = st.session_state.get("sala_reservar_id")
data_prefill = st.session_state.pop("reservar_data_prefill", None)
if data_prefill and data_prefill < date.today():
    data_prefill = None
hora_inicio_prefill = st.session_state.pop("reservar_hora_inicio_prefill", None)
hora_fim_prefill = st.session_state.pop("reservar_hora_fim_prefill", None)

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

col1, col2 = st.columns(2)

with col1:
    st.write(
        f"👥 Capacidade: {sala['capacidade']} pessoas"
    )

with col2:
    st.write(
        f"📍 {sala['predio']} - {sala['andar']}º andar"
    )

st.divider()

data_reserva_preview = st.date_input(
    "Data da reserva",
    min_value=date.today(),
    value=data_prefill if data_prefill else date.today(),
    key="data_preview"
)

# Valores padrão do formulário variam conforme o dia
# para já nascerem dentro da janela permitida.
if data_reserva_preview.weekday() == 5:
    hora_inicio_padrao = time(8, 0)
    hora_fim_padrao = time(10, 0)

    st.caption(
        "⏰ Aos sábados, reservas são permitidas apenas "
        "entre 08:00 e 18:00."
    )
else:
    hora_inicio_padrao = time(19, 0)
    hora_fim_padrao = time(21, 45)

    st.caption(
        "⏰ De segunda a sexta, reservas são permitidas "
        "entre 19:00 e 21:45."
    )

if hora_inicio_prefill:
    hora_inicio_padrao = hora_inicio_prefill
if hora_fim_prefill:
    hora_fim_padrao = hora_fim_prefill

with st.form("form_reserva"):

    data_reserva = st.date_input(
        "Confirmar data da reserva",
        value=data_reserva_preview,
        min_value=date.today()
    )

    col_inicio, col_fim = st.columns(2)

    with col_inicio:
        hora_inicio = st.time_input(
            "Horário de início",
            value=hora_inicio_padrao
        )

    with col_fim:
        hora_fim = st.time_input(
            "Horário de término",
            value=hora_fim_padrao
        )

    enviado = st.form_submit_button(
        "Confirmar reserva",
        type="primary"
    )


if enviado:
    try:
        nova_reserva = criar_reserva(
            sala_id=sala_id,
            id_user=usuario_atual["idUser"],
            data_reserva=data_reserva,
            hora_inicio=hora_inicio,
            hora_fim=hora_fim,
        )

        st.success(
            f"✅ Reserva #{nova_reserva['idReserva']} "
            f"confirmada com sucesso para "
            f"{data_reserva.strftime('%d/%m/%Y')} das "
            f"{hora_inicio.strftime('%H:%M')} às "
            f"{hora_fim.strftime('%H:%M')}."
        )

        st.balloons()

    except RegraNegocioError as erro:
        st.error(
            f"❌ Não foi possível concluir a reserva: {erro}"
        )