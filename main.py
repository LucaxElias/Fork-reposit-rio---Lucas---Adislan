import streamlit as st

st.set_page_config(
    page_title="Reserva de Salas",
    page_icon="🏫",
    layout="wide"
)

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

pagina_atual = st.navigation(
    [home, salas, detalhes_sala, reservar, minhas_reservas]
)

pagina_atual.run()