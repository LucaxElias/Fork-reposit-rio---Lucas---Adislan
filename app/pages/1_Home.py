from datetime import date, datetime, timedelta

import streamlit as st

from app.services.usuarios import listar_usuarios
from app.services.reservas import listar_reservas_por_usuario, FORMATO_DATA
from app.services.salas import listar_salas, buscar_sala_por_id
from app.services.validacao import STATUS_RESERVA_CONFIRMADA, STATUS_SALA_DISPONIVEL
from app.utils.session import definir_usuario_atual, obter_usuario_atual
from app.utils.helpers import badge_status, formatar_data_extenso

st.title("Sistema de Reserva de Salas")

usuario_atual = obter_usuario_atual()

if usuario_atual is None:
    st.write("Bem-vindo ao sistema de reserva de salas.")
    st.info("Utilize o menu lateral para navegar pelo sistema.")
else:
    st.subheader(f"Olá, {usuario_atual['nome']}! 👋")
    st.caption(formatar_data_extenso(date.today(), com_dia_semana=True))

    df_reservas = listar_reservas_por_usuario(usuario_atual["idUser"])
    df_reservas = df_reservas[df_reservas["status"] == STATUS_RESERVA_CONFIRMADA].copy()

    hoje = date.today()
    proxima_reserva = None
    reservas_30_dias = 0

    if not df_reservas.empty:
        df_reservas["data_dt"] = df_reservas["data"].apply(
            lambda d: datetime.strptime(d, FORMATO_DATA).date()
        )
        df_futuras = df_reservas[df_reservas["data_dt"] >= hoje].sort_values(
            ["data_dt", "horaInicio"]
        )

        if not df_futuras.empty:
            proxima_reserva = df_futuras.iloc[0]

        reservas_30_dias = len(
            df_futuras[df_futuras["data_dt"] <= hoje + timedelta(days=30)]
        )

    df_todas_salas = listar_salas()
    df_disponiveis = df_todas_salas[df_todas_salas["status"] == STATUS_SALA_DISPONIVEL]

    col1, col2, col3 = st.columns(3)

    with col1:
        if proxima_reserva is not None:
            sala_proxima = buscar_sala_por_id(proxima_reserva["idSala"])
            nome_sala_proxima = sala_proxima["nome"] if sala_proxima else f"Sala #{proxima_reserva['idSala']}"
            st.metric(
                "Próxima reserva",
                f"{proxima_reserva['data']} {proxima_reserva['horaInicio'][:5]}",
            )
            st.caption(nome_sala_proxima)
        else:
            st.metric("Próxima reserva", "—")
            st.caption("Nenhuma reserva futura")

    with col2:
        st.metric("Reservas futuras", reservas_30_dias)
        st.caption("Nos próximos 30 dias")

    with col3:
        st.metric("Disponíveis agora", len(df_disponiveis))
        st.caption(f"de {len(df_todas_salas)} ambiente(s)")

    if proxima_reserva is not None:
        st.divider()
        st.write("**Próxima reserva**")

        with st.container(border=True):
            col_info, col_status = st.columns([3, 1])

            with col_info:
                st.markdown(f"### {nome_sala_proxima}")
                st.write(
                    f"📅 {proxima_reserva['data']}  •  "
                    f"🕐 {proxima_reserva['horaInicio'][:5]} - "
                    f"{proxima_reserva['horaFim'][:5]}"
                )

            with col_status:
                st.markdown(
                    badge_status(proxima_reserva["status"]),
                    unsafe_allow_html=True,
                )

            col_btn1, col_btn2 = st.columns(2)

            with col_btn1:
                if st.button("Ver disponibilidade", use_container_width=True):
                    st.session_state["sala_selecionada_id"] = proxima_reserva["idSala"]
                    st.switch_page("app/pages/7_Disponibilidade.py")

            with col_btn2:
                if st.button("Minhas reservas", use_container_width=True):
                    st.switch_page("app/pages/5_Minhas_Reservas.py")

st.divider()

st.subheader("👤 " + ("Trocar usuário" if usuario_atual else "Selecionar usuário"))

usuarios_df = listar_usuarios()

with st.container(border=True):
    if usuarios_df.empty:
        st.error(
            "Nenhum usuário encontrado em data/usuarios.csv. "
            "Cadastre usuários para poder simular uma sessão."
        )
    else:
        opcoes = usuarios_df.apply(
            lambda linha: f"{linha['idUser']} - {linha['nome']} ({linha['role']})", axis=1
        ).tolist()

        indice_padrao = 0
        if usuario_atual is not None:
            for i, linha in usuarios_df.iterrows():
                if linha["idUser"] == str(usuario_atual["idUser"]):
                    indice_padrao = i
                    break

        escolha = st.selectbox(
            "Simular sessão como:",
            options=range(len(opcoes)),
            format_func=lambda i: opcoes[i],
            index=indice_padrao,
        )

        if st.button("Fixar usuário", type="primary"):
            usuario_escolhido = usuarios_df.iloc[escolha].to_dict()
            definir_usuario_atual(usuario_escolhido)
            st.success(f"Usuário fixado: {usuario_escolhido['nome']}")
            st.rerun()

        usuario_atual = obter_usuario_atual()
        if usuario_atual is not None:
            st.success(
                f"Sessão atual: **{usuario_atual['nome']}** "
                f"(id {usuario_atual['idUser']}, papel: {usuario_atual['role']})"
            )
        else:
            st.warning("Nenhum usuário fixado ainda. Selecione um acima para poder navegar pelo sistema.")
