"""
Utilitários de apresentação compartilhados entre as páginas.
Injeta o CSS do tema visual (baseado no protótipo Figma "LarpReserve").
"""

import streamlit as st

CORES_STATUS = {
    "Disponivel": ("#dcfce7", "#15803d"),
    "Manutencao": ("#fef3c7", "#b45309"),
    "Indisponivel": ("#fee2e2", "#b91c1c"),
    "Confirmada": ("#dbeafe", "#1d4ed8"),
    "Pendente": ("#fef3c7", "#b45309"),
    "Concluida": ("#f1f5f9", "#475569"),
    "Cancelada": ("#fee2e2", "#b91c1c"),
    "Ocupado": ("#fee2e2", "#b91c1c"),
}

LABELS_STATUS = {
    "Disponivel": "Disponível",
    "Manutencao": "Manutenção",
    "Indisponivel": "Indisponível",
    "Concluida": "Concluída",
}


def badge_status(status: str) -> str:
    """Retorna o HTML de um badge colorido para um valor de status do CSV."""
    bg, cor = CORES_STATUS.get(status, ("#f1f5f9", "#475569"))
    texto = LABELS_STATUS.get(status, status)
    return (
        f'<span style="background:{bg};color:{cor};padding:4px 12px;'
        f'border-radius:999px;font-size:0.85rem;font-weight:600;'
        f'white-space:nowrap;">{texto}</span>'
    )


def tag_neutra(texto: str) -> str:
    """Retorna o HTML de uma tag neutra (tipo de sala, equipamento, etc.)."""
    return (
        f'<span style="background:#f1f5f9;color:#475569;padding:3px 10px;'
        f'border-radius:8px;font-size:0.78rem;font-weight:500;'
        f'white-space:nowrap;margin-right:6px;display:inline-block;'
        f'margin-bottom:4px;">{texto}</span>'
    )


def barra_status(status: str) -> str:
    """Retorna o HTML de uma barra colorida (accent) para o topo de um card."""
    _, cor = CORES_STATUS.get(status, ("#f1f5f9", "#475569"))
    return (
        f'<div style="height:4px;width:100%;background:{cor};'
        f'border-radius:4px;margin-bottom:12px;"></div>'
    )


MESES_PT = {
    1: "janeiro", 2: "fevereiro", 3: "março", 4: "abril",
    5: "maio", 6: "junho", 7: "julho", 8: "agosto",
    9: "setembro", 10: "outubro", 11: "novembro", 12: "dezembro",
}

DIAS_SEMANA_PT = [
    "Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira",
    "Sexta-feira", "Sábado", "Domingo",
]


def formatar_data_extenso(data, com_dia_semana: bool = False) -> str:
    """Formata uma data como 'DD de mês de AAAA' em português, sem depender do locale do SO."""
    texto = f"{data.day:02d} de {MESES_PT[data.month]} de {data.year}"
    if com_dia_semana:
        texto = f"{DIAS_SEMANA_PT[data.weekday()]}, {texto}"
    return texto


def injetar_estilos() -> None:
    """Aplica o CSS do tema visual em toda a aplicação. Chamar uma vez por página."""
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

        html, body, [class*="css"] {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }

        /* Cabecalho das paginas */
        h1, h2, h3 {
            color: #0f172a;
            font-weight: 700;
        }

        /* Sidebar: logo e blocos de navegacao */
        [data-testid="stSidebarNav"] { padding-top: 0.5rem; }

        [data-testid="stSidebar"] hr {
            border-color: rgba(255,255,255,0.08);
        }

        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] span {
            color: #e2e8f0;
        }

        /* Botoes primarios */
        button[kind="primary"] {
            background-color: #2563eb;
            border: none;
            border-radius: 8px;
            font-weight: 600;
        }
        button[kind="primary"]:hover {
            background-color: #1d4ed8;
        }

        button[kind="secondary"] {
            border-radius: 8px;
            border-color: #e2e8f0;
            font-weight: 600;
        }

        /* Cards (st.container(border=True)) */
        [data-testid="stVerticalBlockBorderWrapper"] {
            border-radius: 14px !important;
            border: 1px solid #e2e8f0 !important;
            background: #ffffff;
        }

        /* Metricas em estilo card */
        [data-testid="stMetric"] {
            background: #ffffff;
            border-radius: 14px;
            padding: 1rem 1.2rem;
            border: 1px solid #e2e8f0;
        }
        [data-testid="stMetricLabel"] {
            color: #64748b;
        }

        /* Alertas com cantos mais arredondados, alinhado ao restante da UI */
        [data-testid="stAlert"] {
            border-radius: 10px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
