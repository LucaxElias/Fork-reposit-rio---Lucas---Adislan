"""
Módulo de serviços relacionados aos equipamentos vinculados a cada sala.
Junta `data/sala_equipamento.csv` com `data/equipamentos.csv`.

Colunas reais dos CSVs:
equipamentos.csv: idEquipamento;nome;descricao;estadoConservacao
sala_equipamento.csv: idSala;idEquipamento;idTipoSala;quantidade
"""

import os

import pandas as pd

CAMINHO_EQUIPAMENTOS_CSV = os.path.join("data", "equipamentos.csv")
CAMINHO_SALA_EQUIPAMENTO_CSV = os.path.join("data", "sala_equipamento.csv")
SEPARADOR = ";"

COLUNAS_EQUIPAMENTOS_DA_SALA = ["nome", "quantidade"]


def _carregar_equipamentos() -> pd.DataFrame:
    if not os.path.exists(CAMINHO_EQUIPAMENTOS_CSV):
        return pd.DataFrame(columns=["idEquipamento", "nome", "descricao", "estadoConservacao"])
    return pd.read_csv(
        CAMINHO_EQUIPAMENTOS_CSV, sep=SEPARADOR, dtype={"idEquipamento": str}
    )


def _carregar_sala_equipamento() -> pd.DataFrame:
    if not os.path.exists(CAMINHO_SALA_EQUIPAMENTO_CSV):
        return pd.DataFrame(columns=["idSala", "idEquipamento", "idTipoSala", "quantidade"])
    return pd.read_csv(
        CAMINHO_SALA_EQUIPAMENTO_CSV,
        sep=SEPARADOR,
        dtype={"idSala": str, "idEquipamento": str},
    )


def obter_equipamentos_da_sala(id_sala) -> pd.DataFrame:
    """Retorna os equipamentos (nome + quantidade) vinculados a uma sala."""
    id_sala = str(id_sala)
    vinculos = _carregar_sala_equipamento()
    vinculos = vinculos[vinculos["idSala"] == id_sala]

    if vinculos.empty:
        return pd.DataFrame(columns=COLUNAS_EQUIPAMENTOS_DA_SALA)

    equipamentos = _carregar_equipamentos()
    resultado = vinculos.merge(equipamentos, on="idEquipamento", how="left")
    return resultado[COLUNAS_EQUIPAMENTOS_DA_SALA].reset_index(drop=True)
