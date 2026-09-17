import streamlit as st

from app.utils.helpers import injetar_estilos

st.set_page_config(
    page_title="Reserva de Salas",
    page_icon="🏫",
    layout="wide"
)

injetar_estilos()

home = st.Page(
    "app/pages/1_Home.py",
    title="Home",
    icon="🏠",
    default=True
)

salas = st.Page(
    "app/pages/2_Salas.py",
    title="Salas",
    icon="🏢"
)

detalhes_sala = st.Page(
    "app/pages/3_Detalhes_Sala.py",
    title="Detalhes Sala",
    icon="🔍"
)

reservar = st.Page(
    "app/pages/4_Reservar.py",
    title="Reservar",
    icon="📅"
)

minhas_reservas = st.Page(
    "app/pages/5_Minhas_Reservas.py",
    title="Minhas Reservas",
    icon="🗂️"
)

perfil = st.Page(
    "app/pages/6_Perfil.py",
    title="Perfil",
    icon="👤"
)

disponibilidade = st.Page(
    "app/pages/7_Disponibilidade.py",
    title="Disponibilidade",
    icon="📆"
)

pagina_atual = st.navigation(
    [home, salas, detalhes_sala, reservar, disponibilidade, minhas_reservas, perfil]
)

pagina_atual.run()