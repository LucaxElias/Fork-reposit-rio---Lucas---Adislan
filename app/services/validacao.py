"""
Módulo de validações relacionadas às regras de negócio de reservas
de salas e laboratórios da UNISAPIENS.

Baseado no documento "Regras de Negócio - Sistema de Reserva de Salas
e Laboratórios da UNISAPIENS", com os seguintes ajustes institucionais:

- Reservas permitidas de segunda a sábado (domingo bloqueado).
- Horário permitido em dias de semana: 19:00 às 21:45.
- Horário permitido aos sábados: 08:00 às 18:00 (período de aula aos sábados).
- Valores de status das salas seguem o CSV real, sem acentuação
  (Disponivel, Manutencao, Indisponivel).
"""

from datetime import datetime, date, time
from typing import Optional


# ------------------------------------------------------------------
# Constantes de regras de negócio
# ------------------------------------------------------------------

DURACAO_MINIMA_MINUTOS = 30
DURACAO_MAXIMA_MINUTOS = 4 * 60  # 4 horas

# Horário permitido em dias de semana (segunda a sexta)
HORARIO_INICIO_SEMANA = time(19, 0)
HORARIO_FIM_SEMANA = time(21, 45)

# Horário permitido aos sábados (período em que há aula aos sábados)
HORARIO_INICIO_SABADO = time(8, 0)
HORARIO_FIM_SABADO = time(18, 0)

SABADO = 5  # date.weekday() == 5 -> sábado
DOMINGO = 6  # date.weekday() == 6 -> domingo

# Regra 7 (com exceção institucional): reservas permitidas de segunda
# a sábado. Domingo continua bloqueado.
DIAS_PERMITIDOS_RESERVA = {0, 1, 2, 3, 4, 5}  # segunda(0) ... sábado(5)

# Valores sem acento, para bater exatamente com o CSV real (salas.csv)
STATUS_SALA_DISPONIVEL = "Disponivel"
STATUS_SALA_MANUTENCAO = "Manutencao"
STATUS_SALA_INDISPONIVEL = "Indisponivel"

STATUS_RESERVA_CONFIRMADA = "Confirmada"
STATUS_RESERVA_CANCELADA = "Cancelada"


class RegraNegocioError(Exception):
    """Exceção lançada quando uma regra de negócio é violada."""
    pass


# ------------------------------------------------------------------
# Validações de horário
# ------------------------------------------------------------------

def validar_horario_inicio_fim(hora_inicio: time, hora_fim: time) -> None:
    """Regra 2: o horário de início deve ser menor que o horário de fim."""
    if hora_inicio >= hora_fim:
        raise RegraNegocioError(
            "O horário de início deve ser menor que o horário de fim."
        )


def calcular_duracao_minutos(hora_inicio: time, hora_fim: time) -> int:
    """Calcula a duração da reserva em minutos."""
    inicio_dt = datetime.combine(date.today(), hora_inicio)
    fim_dt = datetime.combine(date.today(), hora_fim)
    return int((fim_dt - inicio_dt).total_seconds() // 60)


def validar_duracao(hora_inicio: time, hora_fim: time) -> None:
    """
    Regra 3: duração mínima de uma reserva é de 30 minutos.
    Regra 4: duração máxima de uma reserva é de 4 horas.
    """
    duracao = calcular_duracao_minutos(hora_inicio, hora_fim)

    if duracao < DURACAO_MINIMA_MINUTOS:
        raise RegraNegocioError(
            f"A duração mínima de uma reserva é de {DURACAO_MINIMA_MINUTOS} minutos."
        )

    if duracao > DURACAO_MAXIMA_MINUTOS:
        raise RegraNegocioError(
            f"A duração máxima de uma reserva é de {DURACAO_MAXIMA_MINUTOS // 60} horas."
        )


def validar_dia_permitido(data_reserva: date) -> None:
    """
    Regra 7: o documento de regras prevê como padrão apenas dias úteis
    (segunda a sexta), mas define explicitamente a exceção 'salvo regra
    específica da instituição'. A UNISAPIENS libera também o sábado,
    mantendo domingo bloqueado.
    """
    if data_reserva.weekday() not in DIAS_PERMITIDOS_RESERVA:
        raise RegraNegocioError(
            "As reservas só podem ser feitas de segunda a sábado."
        )


# Alias para compatibilidade, caso algo já chame o nome antigo
validar_dia_util = validar_dia_permitido


def obter_horario_permitido(data_reserva: date) -> tuple:
    """
    Retorna (horario_inicio_permitido, horario_fim_permitido) de acordo
    com o dia da semana da reserva.
    Regra 8 (semana): 19:00 às 21:45.
    Regra 8 (sábado): 08:00 às 18:00 - período em que há aula aos sábados.
    """
    if data_reserva.weekday() == SABADO:
        return HORARIO_INICIO_SABADO, HORARIO_FIM_SABADO
    return HORARIO_INICIO_SEMANA, HORARIO_FIM_SEMANA


def validar_horario_permitido(hora_inicio: time, hora_fim: time, data_reserva: date) -> None:
    """
    Regra 8: valida se o horário da reserva está dentro da janela
    permitida, que varia conforme o dia (semana x sábado).
    """
    inicio_permitido, fim_permitido = obter_horario_permitido(data_reserva)

    if hora_inicio < inicio_permitido or hora_fim > fim_permitido:
        raise RegraNegocioError(
            "O horário de reserva deve estar entre "
            f"{inicio_permitido.strftime('%H:%M')} e "
            f"{fim_permitido.strftime('%H:%M')}"
            + (" aos sábados." if data_reserva.weekday() == SABADO else ".")
        )


# ------------------------------------------------------------------
# Validações de status
# ------------------------------------------------------------------

def validar_status_sala_disponivel(status_sala: str) -> None:
    """
    Regra 5: só é permitido reservar salas com status Disponivel.
    Regra 6: não é permitido reservar salas com status Manutencao ou Indisponivel.
    """
    if status_sala != STATUS_SALA_DISPONIVEL:
        raise RegraNegocioError(
            f"A sala não pode ser reservada pois está com status '{status_sala}'."
        )


def validar_status_reserva_confirmada(status_reserva: str) -> None:
    """Regra 9: só é possível cancelar reservas com status Confirmada."""
    if status_reserva != STATUS_RESERVA_CONFIRMADA:
        raise RegraNegocioError(
            "Só é possível cancelar reservas com status 'Confirmada'."
        )


# ------------------------------------------------------------------
# Conflito de horário
# ------------------------------------------------------------------

def horarios_conflitam(
    inicio_a: time, fim_a: time, inicio_b: time, fim_b: time
) -> bool:
    """
    Verifica se dois intervalos de horário se sobrepõem.
    Regra 1: uma sala não pode ter duas reservas confirmadas
    sobrepostas no mesmo horário.
    """
    return inicio_a < fim_b and inicio_b < fim_a


def validar_conflito_horario(
    sala_id,
    data_reserva: date,
    hora_inicio: time,
    hora_fim: time,
    reservas_existentes: list,
    reserva_id_ignorar: Optional[str] = None,
) -> None:
    """
    Regra 1: verifica se já existe reserva Confirmada para a mesma sala,
    na mesma data, com sobreposição de horário.

    `reservas_existentes` deve ser uma lista de dicts já normalizados
    com as chaves: id, sala_id, data, hora_inicio, hora_fim, status
    (ver reservas.py -> _carregar_reservas_tipadas).

    `reserva_id_ignorar` é útil ao editar uma reserva existente, para
    não comparar a reserva consigo mesma.
    """
    for reserva in reservas_existentes:
        if reserva_id_ignorar is not None and str(reserva["id"]) == str(reserva_id_ignorar):
            continue
        if str(reserva["sala_id"]) != str(sala_id):
            continue
        if reserva["status"] != STATUS_RESERVA_CONFIRMADA:
            continue
        if reserva["data"] != data_reserva:
            continue

        if horarios_conflitam(
            hora_inicio, hora_fim, reserva["hora_inicio"], reserva["hora_fim"]
        ):
            raise RegraNegocioError(
                "Já existe uma reserva confirmada para esta sala neste horário."
            )


# ------------------------------------------------------------------
# Validação completa (agregadora)
# ------------------------------------------------------------------

def validar_reserva(
    sala_id,
    status_sala: str,
    data_reserva: date,
    hora_inicio: time,
    hora_fim: time,
    reservas_existentes: list,
    reserva_id_ignorar: Optional[str] = None,
) -> None:
    """
    Executa todas as validações necessárias antes de confirmar uma
    reserva. Lança RegraNegocioError na primeira regra violada.

    Recebe `sala_id` e `status_sala` separadamente (em vez de um dict
    de sala) para não depender do nome exato das colunas do CSV.
    """
    validar_horario_inicio_fim(hora_inicio, hora_fim)
    validar_duracao(hora_inicio, hora_fim)
    validar_dia_permitido(data_reserva)
    validar_horario_permitido(hora_inicio, hora_fim, data_reserva)
    validar_status_sala_disponivel(status_sala)
    validar_conflito_horario(
        sala_id,
        data_reserva,
        hora_inicio,
        hora_fim,
        reservas_existentes,
        reserva_id_ignorar=reserva_id_ignorar,
    )