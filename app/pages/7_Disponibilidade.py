import streamlit as st
from datetime import date, datetime, timedelta

from app.services.salas import buscar_sala_por_id, listar_salas
from app.services.reservas import listar_reservas_por_sala, parse_hora
from app.services.usuarios import buscar_usuario_por_id
from app.services.validacao import obter_horario_permitido, horarios_conflitam
from app.utils.session import exigir_usuario_selecionado
from app.utils.helpers import badge_status, formatar_data_extenso

st.set_page_config(
    page_title="Disponibilidade - UNISAPIENS",
    page_icon="📆",
    layout="wide"
)

usuario_atual = exigir_usuario_selecionado()

st.title("📆 Disponibilidade")
st.caption("Verifique horários disponíveis em tempo real, por sala e dia")

df_salas = listar_salas()

if df_salas.empty:
    st.error("Nenhuma sala cadastrada.")
    st.stop()

opcoes_ids = df_salas["idSala"].tolist()
sala_id_padrao = st.session_state.get("sala_selecionada_id")
indice_padrao = (
    opcoes_ids.index(sala_id_padrao) if sala_id_padrao in opcoes_ids else 0
)

sala_id = st.selectbox(
    "Sala",
    options=opcoes_ids,
    index=indice_padrao,
    format_func=lambda i: df_salas[df_salas["idSala"] == i]["nome"].values[0],
)
sala = buscar_sala_por_id(sala_id)
st.session_state["sala_selecionada_id"] = sala_id

st.divider()

if "disponibilidade_data" not in st.session_state:
    st.session_state["disponibilidade_data"] = date.today()

data_base = st.session_state["disponibilidade_data"]
inicio_semana = data_base - timedelta(days=(data_base.weekday() + 1) % 7)
dias_semana = [inicio_semana + timedelta(days=i) for i in range(7)]
nomes_dias = ["Dom", "Seg", "Ter", "Qua", "Qui", "Sex", "Sáb"]

col_prev, col_dias, col_next = st.columns([1, 10, 1])

with col_prev:
    if st.button("◀", key="semana_anterior", use_container_width=True):
        st.session_state["disponibilidade_data"] = data_base - timedelta(days=7)
        st.rerun()

with col_next:
    if st.button("▶", key="semana_seguinte", use_container_width=True):
        st.session_state["disponibilidade_data"] = data_base + timedelta(days=7)
        st.rerun()

with col_dias:
    cols = st.columns(7)
    for i, dia in enumerate(dias_semana):
        with cols[i]:
            selecionado = dia == data_base
            if st.button(
                f"{nomes_dias[i]} {dia.day:02d}",
                key=f"dia_{dia.isoformat()}",
                type="primary" if selecionado else "secondary",
                use_container_width=True,
            ):
                st.session_state["disponibilidade_data"] = dia
                st.rerun()

st.divider()

data_selecionada = st.session_state["disponibilidade_data"]

st.subheader(formatar_data_extenso(data_selecionada))

if data_selecionada.weekday() == 6:
    st.info("Não há reservas permitidas aos domingos.")
else:
    inicio_permitido, fim_permitido = obter_horario_permitido(data_selecionada)

    reservas_do_dia = listar_reservas_por_sala(sala_id, apenas_confirmadas=True)
    data_formatada = data_selecionada.strftime("%d/%m/%Y")
    reservas_do_dia = reservas_do_dia[reservas_do_dia["data"] == data_formatada]

    hora_atual = inicio_permitido
    while hora_atual < fim_permitido:
        fim_slot = (
            datetime.combine(date.today(), hora_atual) + timedelta(hours=1)
        ).time()
        if fim_slot > fim_permitido:
            fim_slot = fim_permitido

        ocupante = None
        for _, reserva in reservas_do_dia.iterrows():
            r_inicio = parse_hora(reserva["horaInicio"])
            r_fim = parse_hora(reserva["horaFim"])
            if horarios_conflitam(hora_atual, fim_slot, r_inicio, r_fim):
                ocupante = reserva
                break

        col_hora, col_status, col_acao = st.columns([1, 2, 2])

        with col_hora:
            st.write(f"**{hora_atual.strftime('%H:%M')}**")

        with col_status:
            if ocupante is not None:
                st.markdown(badge_status("Ocupado"), unsafe_allow_html=True)
                usuario_reserva = buscar_usuario_por_id(ocupante["idUser"])
                nome_ocupante = (
                    usuario_reserva["nome"]
                    if usuario_reserva
                    else f"Usuário #{ocupante['idUser']}"
                )
                st.caption(f"Reservado por {nome_ocupante}")
            else:
                st.markdown(badge_status("Disponivel"), unsafe_allow_html=True)

        with col_acao:
            if ocupante is None and data_selecionada >= date.today():
                if st.button("Reservar", key=f"reservar_{hora_atual.isoformat()}"):
                    st.session_state["sala_reservar_id"] = sala_id
                    st.session_state["reservar_data_prefill"] = data_selecionada
                    st.session_state["reservar_hora_inicio_prefill"] = hora_atual
                    st.session_state["reservar_hora_fim_prefill"] = fim_slot
                    st.switch_page("app/pages/4_Reservar.py")

        hora_atual = fim_slot
