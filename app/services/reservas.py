"""
Módulo de serviços relacionados às reservas de salas e laboratórios.

Colunas reais do CSV:
idReserva;idUser;idSala;data;horaInicio;horaFim;status;criado_em

Observações sobre o CSV real:
- Datas no formato DD/MM/YYYY.
- Horários vêm inconsistentes: algumas linhas "HH:MM", outras "HH:MM:SS".
  O parser abaixo aceita os dois formatos.
"""

import os
from datetime import datetime, date, time
from typing import Optional

import pandas as pd

from app.services.salas import buscar_sala_por_id
from app.services.validacao import (
    validar_reserva,
    validar_status_reserva_confirmada,
    RegraNegocioError,
    STATUS_RESERVA_CONFIRMADA,
    STATUS_RESERVA_CANCELADA,
)

CAMINHO_RESERVAS_CSV = os.path.join("data", "reservas.csv")
SEPARADOR = ";"

COLUNAS_RESERVAS = [
    "idReserva", "idUser", "idSala", "data",
    "horaInicio", "horaFim", "status", "criado_em",
]

FORMATO_DATA = "%d/%m/%Y"
FORMATOS_HORA = ("%H:%M:%S", "%H:%M")  # tenta nessa ordem


def parse_hora(valor: str) -> time:
    """Converte string de hora para time, aceitando 'HH:MM' e 'HH:MM:SS'."""
    valor = str(valor).strip()
    for formato in FORMATOS_HORA:
        try:
            return datetime.strptime(valor, formato).time()
        except ValueError:
            continue
    raise RegraNegocioError(f"Formato de hora inválido: '{valor}'.")


# ------------------------------------------------------------------
# Leitura / escrita do CSV
# ------------------------------------------------------------------

def _carregar_reservas_bruto() -> pd.DataFrame:
    """Carrega o CSV de reservas como strings, sem conversão de tipos."""
    if not os.path.exists(CAMINHO_RESERVAS_CSV):
        return pd.DataFrame(columns=COLUNAS_RESERVAS)
    return pd.read_csv(CAMINHO_RESERVAS_CSV, sep=SEPARADOR, dtype=str)


def _salvar_reservas(df: pd.DataFrame) -> None:
    df.to_csv(CAMINHO_RESERVAS_CSV, sep=SEPARADOR, index=False)


def _linha_para_dict_tipado(linha: dict) -> dict:
    """
    Converte uma linha do CSV (strings) para o formato normalizado
    esperado por validacao.py: id, sala_id, data, hora_inicio, hora_fim, status.
    """
    return {
        "id": linha["idReserva"],
        "sala_id": linha["idSala"],
        "usuario_id": linha["idUser"],
        "data": datetime.strptime(linha["data"], FORMATO_DATA).date(),
        "hora_inicio": parse_hora(linha["horaInicio"]),
        "hora_fim": parse_hora(linha["horaFim"]),
        "status": linha["status"],
    }


def _carregar_reservas_tipadas() -> list:
    """Retorna a lista de reservas normalizada, pronta para validacao.py."""
    df = _carregar_reservas_bruto()
    return [_linha_para_dict_tipado(row) for row in df.to_dict("records")]


# ------------------------------------------------------------------
# Consultas
# ------------------------------------------------------------------

def listar_reservas() -> pd.DataFrame:
    return _carregar_reservas_bruto().reset_index(drop=True)


def buscar_reserva_por_id(reserva_id) -> Optional[dict]:
    df = _carregar_reservas_bruto()
    reserva_id = str(reserva_id)
    resultado = df[df["idReserva"] == reserva_id]

    if resultado.empty:
        return None

    return resultado.iloc[0].to_dict()


def listar_reservas_por_usuario(id_user) -> pd.DataFrame:
    """Reservas de um usuário específico (tela 'Minhas Reservas')."""
    df = _carregar_reservas_bruto()
    id_user = str(id_user)
    return df[df["idUser"] == id_user].reset_index(drop=True)


def listar_reservas_por_sala(sala_id, apenas_confirmadas: bool = True) -> pd.DataFrame:
    """Reservas de uma sala específica (tela de detalhes da sala)."""
    df = _carregar_reservas_bruto()
    sala_id = str(sala_id)
    df = df[df["idSala"] == sala_id]

    if apenas_confirmadas:
        df = df[df["status"] == STATUS_RESERVA_CONFIRMADA]

    return df.reset_index(drop=True)


# ------------------------------------------------------------------
# Criação de reserva
# ------------------------------------------------------------------

def criar_reserva(
    sala_id,
    id_user,
    data_reserva: date,
    hora_inicio: time,
    hora_fim: time,
) -> dict:
    """
    Cria uma nova reserva, validando todas as regras de negócio antes
    de persistir (Regras 1 a 8). Lança RegraNegocioError se alguma
    validação falhar.
    """
    sala = buscar_sala_por_id(sala_id)
    if sala is None:
        raise RegraNegocioError(f"Sala com id '{sala_id}' não encontrada.")

    reservas_existentes = _carregar_reservas_tipadas()

    validar_reserva(
        sala_id=sala["idSala"],
        status_sala=sala["status"],
        data_reserva=data_reserva,
        hora_inicio=hora_inicio,
        hora_fim=hora_fim,
        reservas_existentes=reservas_existentes,
    )

    df = _carregar_reservas_bruto()

    if df.empty:
        novo_id = "1"
    else:
        novo_id = str(df["idReserva"].astype(int).max() + 1)

    nova_reserva = {
        "idReserva": novo_id,
        "idUser": str(id_user),
        "idSala": str(sala_id),
        "data": data_reserva.strftime(FORMATO_DATA),
        "horaInicio": hora_inicio.strftime("%H:%M:%S"),
        "horaFim": hora_fim.strftime("%H:%M:%S"),
        "status": STATUS_RESERVA_CONFIRMADA,
        "criado_em": date.today().strftime(FORMATO_DATA),
    }

    df = pd.concat([df, pd.DataFrame([nova_reserva])], ignore_index=True)
    _salvar_reservas(df)

    return nova_reserva


# ------------------------------------------------------------------
# Cancelamento de reserva
# ------------------------------------------------------------------

def cancelar_reserva(reserva_id, id_user) -> None:
    """
    Cancela uma reserva (Regra 9: só reservas 'Confirmada'; Regra de
    Usuário 3: só o próprio usuário pode cancelar).
    Não apaga o registro — muda status para 'Cancelada' (Regra Técnica 2).
    """
    df = _carregar_reservas_bruto()
    reserva_id = str(reserva_id)
    id_user = str(id_user)

    linha = df[df["idReserva"] == reserva_id]
    if linha.empty:
        raise RegraNegocioError(f"Reserva com id '{reserva_id}' não encontrada.")

    reserva = linha.iloc[0]

    if reserva["idUser"] != id_user:
        raise RegraNegocioError(
            "Apenas o próprio usuário pode cancelar esta reserva."
        )

    validar_status_reserva_confirmada(reserva["status"])

    df.loc[df["idReserva"] == reserva_id, "status"] = STATUS_RESERVA_CANCELADA
    _salvar_reservas(df)