"""
Módulo de serviços relacionados às salas e laboratórios.
Responsável por ler e manipular os dados de `data/salas.csv`.

Colunas reais do CSV:
idSala;nome;capacidade;idTipoSala;predio;andar;status;descricao
"""

import os
from typing import Optional

import pandas as pd

from app.services.validacao import (
    STATUS_SALA_DISPONIVEL,
    STATUS_SALA_MANUTENCAO,
    STATUS_SALA_INDISPONIVEL,
    RegraNegocioError,
)

CAMINHO_SALAS_CSV = os.path.join("data", "salas.csv")
SEPARADOR = ";"

STATUS_VALIDOS = {
    STATUS_SALA_DISPONIVEL,
    STATUS_SALA_MANUTENCAO,
    STATUS_SALA_INDISPONIVEL,
}

COLUNAS_SALAS = [
    "idSala", "nome", "capacidade", "idTipoSala",
    "predio", "andar", "status", "descricao",
]


def _carregar_salas() -> pd.DataFrame:
    if not os.path.exists(CAMINHO_SALAS_CSV):
        return pd.DataFrame(columns=COLUNAS_SALAS)

    return pd.read_csv(CAMINHO_SALAS_CSV, sep=SEPARADOR, dtype={"idSala": str})


def _salvar_salas(df: pd.DataFrame) -> None:
    df.to_csv(CAMINHO_SALAS_CSV, sep=SEPARADOR, index=False)


def listar_salas(apenas_disponiveis: bool = False) -> pd.DataFrame:
    """Retorna todas as salas. Se apenas_disponiveis=True, filtra por status."""
    df = _carregar_salas()
    if apenas_disponiveis:
        df = df[df["status"] == STATUS_SALA_DISPONIVEL]
    return df.reset_index(drop=True)


def buscar_sala_por_id(sala_id) -> Optional[dict]:
    """Retorna os dados de uma sala pelo idSala, ou None se não existir."""
    df = _carregar_salas()
    sala_id = str(sala_id)
    resultado = df[df["idSala"] == sala_id]

    if resultado.empty:
        return None

    return resultado.iloc[0].to_dict()


def filtrar_salas_por_capacidade(capacidade_minima: int) -> pd.DataFrame:
    """Retorna salas com capacidade >= capacidade_minima."""
    df = _carregar_salas()
    if df.empty:
        return df
    df["capacidade"] = df["capacidade"].astype(int)
    return df[df["capacidade"] >= capacidade_minima].reset_index(drop=True)


def filtrar_salas_por_predio(predio: str) -> pd.DataFrame:
    """Retorna salas de um prédio específico (ex.: 'Anexo1', 'Central')."""
    df = _carregar_salas()
    return df[df["predio"] == predio].reset_index(drop=True)


def filtrar_salas_por_tipo(id_tipo_sala) -> pd.DataFrame:
    """Retorna salas de um tipo específico (idTipoSala)."""
    df = _carregar_salas()
    return df[df["idTipoSala"].astype(str) == str(id_tipo_sala)].reset_index(drop=True)


def sala_esta_disponivel(sala_id) -> bool:
    """Verifica se a sala existe e está com status Disponivel (regras 5 e 6)."""
    sala = buscar_sala_por_id(sala_id)
    if sala is None:
        return False
    return sala["status"] == STATUS_SALA_DISPONIVEL


def atualizar_status_sala(sala_id, novo_status: str) -> None:
    """Atualiza o status de uma sala (Disponivel, Manutencao, Indisponivel)."""
    if novo_status not in STATUS_VALIDOS:
        raise RegraNegocioError(
            f"Status inválido para sala: '{novo_status}'. "
            f"Valores aceitos: {', '.join(STATUS_VALIDOS)}."
        )

    df = _carregar_salas()
    sala_id = str(sala_id)

    if sala_id not in df["idSala"].values:
        raise RegraNegocioError(f"Sala com id '{sala_id}' não encontrada.")

    df.loc[df["idSala"] == sala_id, "status"] = novo_status
    _salvar_salas(df)


def cadastrar_sala(
    nome: str,
    capacidade: int,
    id_tipo_sala,
    predio: str,
    andar: int,
    descricao: str = "",
    status: str = STATUS_SALA_DISPONIVEL,
) -> dict:
    """Cadastra uma nova sala, gerando idSala sequencial automaticamente."""
    if status not in STATUS_VALIDOS:
        raise RegraNegocioError(f"Status inválido: '{status}'.")

    df = _carregar_salas()

    if df.empty:
        novo_id = "1"
    else:
        novo_id = str(df["idSala"].astype(int).max() + 1)

    nova_sala = {
        "idSala": novo_id,
        "nome": nome,
        "capacidade": capacidade,
        "idTipoSala": id_tipo_sala,
        "predio": predio,
        "andar": andar,
        "status": status,
        "descricao": descricao,
    }

    df = pd.concat([df, pd.DataFrame([nova_sala])], ignore_index=True)
    _salvar_salas(df)

    return nova_sala