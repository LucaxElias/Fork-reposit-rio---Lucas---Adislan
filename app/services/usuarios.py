"""
Módulo de serviços relacionados aos usuários.
Leitura simples de data/usuarios.csv - usado apenas para simular
o usuário logado no N1 (não há autenticação real).

Colunas reais do CSV:
idUser;nome;email;telefone;role;senha

Observação: mesmo sem autenticação real, a senha nunca deve ser
exibida na interface - as funções abaixo não a expõem em nenhuma
listagem voltada à UI.
"""

import os
import pandas as pd

CAMINHO_USUARIOS_CSV = os.path.join("data", "usuarios.csv")
SEPARADOR = ";"

COLUNAS_USUARIOS = ["idUser", "nome", "email", "telefone", "role", "senha"]

ROLE_ALUNO = "Aluno"
ROLE_PROFESSOR = "Professor"
ROLE_ADMIN = "Admin"


def _carregar_usuarios() -> pd.DataFrame:
    if not os.path.exists(CAMINHO_USUARIOS_CSV):
        return pd.DataFrame(columns=COLUNAS_USUARIOS)
    return pd.read_csv(CAMINHO_USUARIOS_CSV, sep=SEPARADOR, dtype={"idUser": str})


def listar_usuarios() -> pd.DataFrame:
    """
    Retorna todos os usuários cadastrados, SEM a coluna 'senha'
    (não deve ser exibida em nenhuma tela, mesmo em modo simulação).
    """
    df = _carregar_usuarios()
    if "senha" in df.columns:
        df = df.drop(columns=["senha"])
    return df.reset_index(drop=True)


def buscar_usuario_por_id(id_user):
    """
    Retorna os dados de um usuário pelo idUser (sem a senha),
    ou None se não existir.
    """
    df = listar_usuarios()
    id_user = str(id_user)
    resultado = df[df["idUser"] == id_user]

    if resultado.empty:
        return None

    return resultado.iloc[0].to_dict()


def usuario_e_professor(usuario: dict) -> bool:
    """Regra de Prioridade: verifica se o usuário é Professor."""
    return usuario.get("role") == ROLE_PROFESSOR


def usuario_e_admin(usuario: dict) -> bool:
    """
    Regra de Prioridade: verifica se o usuário é Admin/Coordenação
    (pode cancelar qualquer reserva).
    """
    return usuario.get("role") == ROLE_ADMIN