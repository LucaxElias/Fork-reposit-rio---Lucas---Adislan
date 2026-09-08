import pandas as pd
from pathlib import Path
from datetime import date

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"

def carregar_usuarios():
    arquivo = DATA_DIR / "usuarios.csv"
    return pd.read_csv(arquivo)

def carregar_salas():
    arquivo = DATA_DIR / "salas.csv"
    return pd.read_csv(arquivo)

def carregar_equipamentos():
    arquivo = DATA_DIR / "equipamentos.csv"
    return pd.read_csv(arquivo)

def carregar_reservas():
    arquivo = DATA_DIR / "reservas.csv"
    return pd.read_csv(arquivo)

def obter_equipamentos_da_sala(id_sala):
    arquivo = DATA_DIR / "sala_equipamento.csv"
    salas = pd.read_csv(arquivo)
    
    return salas[salas["idSala"] == id_sala]

def obter_reservas_da_sala(id_sala, data = None):
    arquivo = DATA_DIR / "reservas.csv"
    reservas = pd.read_csv(arquivo)
    
    if data is not None:
        return reservas[(reservas["idSala"] == id_sala) & (reservas["data"] == data)]
    
    return reservas[reservas["idSala"] == id_sala]

def verificar_conflito(id_sala, data, hora_inicio, hora_fim):
    arquivo = DATA_DIR / "reservas.csv"
    reservas = pd.read_csv(arquivo)
 
    mesma_sala_e_data = (reservas["idSala"] == id_sala) & (reservas["data"] == data)

    sobreposicao = (reservas["horaInicio"] < hora_fim) & (reservas["horaFim"] > hora_inicio)
    
    return not reservas[mesma_sala_e_data & sobreposicao].empty

def criar_reserva(id_usuario, id_sala, data, hora_inicio, hora_fim):
    arquivo = DATA_DIR / "reservas.csv"

    if (
        arquivo.exists()
        and arquivo.stat().st_size > 0
        and verificar_conflito(id_sala, data, hora_inicio, hora_fim)
    ):
        print("Erro: Horário em conflito com outra reserva.")
        return False

    if arquivo.exists() and arquivo.stat().st_size > 0:
        df_existente = pd.read_csv(arquivo)
        ultimo_id = (
            df_existente["idReserva"].max()
            if not df_existente.empty
            else 0
        )
    else:
        df_existente = pd.DataFrame()
        ultimo_id = 0

    nova_reserva = pd.DataFrame(
        [
            {
                "idReserva": int(ultimo_id + 1),
                "idUser": id_usuario,
                "idSala": id_sala,
                "data": data,
                "horaInicio": hora_inicio,
                "horaFim": hora_fim,
                "status": "Confirmado",
                "criado_em": date.today().isoformat(),
            }
        ]
    )

    df_atualizado = pd.concat(
        [df_existente, nova_reserva], ignore_index=True
    )
    df_atualizado.to_csv(arquivo, index=False)
    return True

def cancelar_reserva(id_reserva):
    arquivo = DATA_DIR / "reservas.csv"
    
    if not arquivo.exists() or arquivo.stat().st_size == 0:
        return False

    df = pd.read_csv(arquivo)

    filtro = df["idReserva"] == id_reserva
    
    if not filtro.any():
        return False

    df.loc[filtro, "status"] = "Cancelada"

    df.to_csv(arquivo, index=False)
    return True