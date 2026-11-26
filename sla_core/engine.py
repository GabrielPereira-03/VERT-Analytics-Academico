"""Motor independente de SLA (v3, em homologação).

Não consulta banco de dados e não altera regras contratuais existentes.
Datas devem ser naive, representando o horário local do contrato.
"""
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from typing import Iterable


@dataclass(frozen=True)
class CalendarioSLA:
    inicio_expediente: time = time(8, 0)
    fim_expediente: time = time(18, 0)
    dias_uteis: frozenset[int] = frozenset({0, 1, 2, 3, 4})
    feriados: frozenset[date] = frozenset()
    horas_corridas: bool = False

    def __post_init__(self):
        if not self.horas_corridas and self.fim_expediente != time(0) and self.inicio_expediente >= self.fim_expediente:
            raise ValueError("Expediente deve terminar depois do início.")
        if not all(0 <= dia <= 6 for dia in self.dias_uteis):
            raise ValueError("Dias úteis devem estar entre 0 e 6.")


def _validar_intervalo(inicio: datetime, fim: datetime) -> None:
    if inicio.tzinfo is not None or fim.tzinfo is not None:
        raise ValueError("Use datetimes naive no horário local do contrato.")
    if fim < inicio:
        raise ValueError("Data final anterior à inicial.")


def mesclar_intervalos(intervalos: Iterable[tuple[datetime, datetime]]) -> list[tuple[datetime, datetime]]:
    """Une pausas coincidentes e adjacentes para evitar desconto duplicado."""
    ordenados = sorted(intervalos, key=lambda p: p[0])
    for ini, fim in ordenados:
        _validar_intervalo(ini, fim)
    unidos = []
    for ini, fim in ordenados:
        if unidos and ini <= unidos[-1][1]:
            anterior, ate = unidos[-1]
            unidos[-1] = (anterior, max(ate, fim))
        else:
            unidos.append((ini, fim))
    return unidos


def _sobreposicao(inicio: datetime, fim: datetime, a: datetime, b: datetime) -> timedelta:
    return max(timedelta(0), min(fim, b) - max(inicio, a))


def _janelas(inicio: datetime, fim: datetime, calendario: CalendarioSLA):
    if calendario.horas_corridas:
        yield inicio, fim
        return
    dia = inicio.date()
    while dia <= fim.date():
        if dia.weekday() in calendario.dias_uteis and dia not in calendario.feriados:
            a = datetime.combine(dia, calendario.inicio_expediente)
            b = datetime.combine(dia + timedelta(days=1) if calendario.fim_expediente == time(0) else dia, calendario.fim_expediente)
            ini, ate = max(a, inicio), min(b, fim)
            if ini < ate:
                yield ini, ate
        dia += timedelta(days=1)


def calcular_tempo_liquido(
    inicio: datetime,
    fim: datetime,
    calendario: CalendarioSLA,
    pausas: Iterable[tuple[datetime, datetime]] = (),
) -> timedelta:
    """Soma janelas válidas e subtrai a união das pausas, sem valores negativos."""
    _validar_intervalo(inicio, fim)
    unidos = mesclar_intervalos(pausas)
    total = timedelta()
    for a, b in _janelas(inicio, fim, calendario):
        duracao = b - a
        desconto = sum((_sobreposicao(a, b, p_ini, p_fim) for p_ini, p_fim in unidos), timedelta())
        total += max(timedelta(), duracao - desconto)
    return total


def percentual_consumido(consumido: timedelta, meta: timedelta) -> float:
    if meta <= timedelta():
        raise ValueError("A meta de SLA deve ser positiva.")
    return round(100 * consumido.total_seconds() / meta.total_seconds(), 2)


def projetar_vencimento(
    inicio: datetime,
    meta: timedelta,
    calendario: CalendarioSLA,
    pausas: Iterable[tuple[datetime, datetime]] = (),
    limite_dias: int = 3660,
) -> datetime:
    """Encontra o vencimento percorrendo janelas válidas e descontando pausas conhecidas.

    A previsão assume que não haverá pausas futuras além das fornecidas.
    """
    if inicio.tzinfo is not None:
        raise ValueError("Use datetimes naive no horário local do contrato.")
    if meta <= timedelta():
        raise ValueError("A meta de SLA deve ser positiva.")
    if limite_dias < 1:
        raise ValueError("Limite de dias inválido.")
    limite = inicio + timedelta(days=limite_dias)
    unidos = mesclar_intervalos(pausas)
    restante = meta
    for a, b in _janelas(inicio, limite, calendario):
        cursor = a
        for p_ini, p_fim in unidos:
            if p_fim <= cursor or p_ini >= b:
                continue
            ate = min(b, max(cursor, p_ini))
            if ate > cursor:
                if ate - cursor >= restante:
                    return cursor + restante
                restante -= ate - cursor
            cursor = max(cursor, min(b, p_fim))
            if cursor >= b:
                break
        if cursor < b:
            if b - cursor >= restante:
                return cursor + restante
            restante -= b - cursor
    raise ValueError("Não foi possível projetar o vencimento no horizonte informado.")
