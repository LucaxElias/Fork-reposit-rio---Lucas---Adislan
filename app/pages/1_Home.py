import streamlit as st

from app.services.usuarios import listar_usuarios
from app.utils.session import definir_usuario_atual, obter_usuario_atual

st.title("Sistema de Reserva de Salas")

st.write(
    "Bem-vindo ao sistema de reserva de salas."
)

st.info(
    "Utilize o menu lateral para navegar pelo sistema."
)

st.divider()

st.subheader("👤 Selecionar usuário")

usuarios_df = listar_usuarios()

if usuarios_df.empty:
    st.error(
        "Nenhum usuário encontrado em data/usuarios.csv. "
        "Cadastre usuários para poder simular uma sessão."
    )
else:
    usuario_atual = obter_usuario_atual()

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