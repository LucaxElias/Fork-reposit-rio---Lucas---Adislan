import streamlit as st

from app.services.usuarios import buscar_usuario_por_id
from app.utils.session import exigir_usuario_selecionado
from app.utils.helpers import tag_neutra

st.set_page_config(
    page_title="Perfil - UNISAPIENS",
    page_icon="👤",
    layout="wide"
)

usuario_sessao = exigir_usuario_selecionado()

st.title("👤 Perfil")
st.caption("Suas informações institucionais")

usuario = buscar_usuario_por_id(usuario_sessao["idUser"]) or usuario_sessao

iniciais = "".join(parte[0].upper() for parte in usuario["nome"].split()[:2])

with st.container(border=True):
    col_avatar, col_nome = st.columns([1, 5])

    with col_avatar:
        st.markdown(
            f'<div style="width:56px;height:56px;border-radius:50%;'
            f'background:#2563eb;color:#ffffff;display:flex;'
            f'align-items:center;justify-content:center;'
            f'font-weight:700;font-size:1.2rem;">{iniciais}</div>',
            unsafe_allow_html=True,
        )

    with col_nome:
        st.subheader(usuario["nome"])
        st.markdown(tag_neutra(usuario["role"]), unsafe_allow_html=True)

    st.divider()

    st.write(f"**Matrícula:** {usuario['idUser']}")
    st.write(f"**E-mail:** {usuario['email']}")
    st.write(f"**Telefone:** {usuario['telefone']}")
    st.write(f"**Perfil:** {usuario['role']}")
