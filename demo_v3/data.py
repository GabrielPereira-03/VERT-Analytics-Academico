"""Dados sintéticos para testes da VERT Analytics v3.0. Sem dados corporativos."""
from datetime import datetime, timedelta

from sla_core.engine import CalendarioSLA, calcular_tempo_liquido, percentual_consumido


TICKETS = [
    {"numero": "900001", "contrato": "CLIENTE-A", "severidade": "Crítico", "estado": "Fechado",
     "abertura": datetime(2026, 11, 16, 8), "fim": datetime(2026, 11, 16, 14),
     "meta_horas": 10, "calendario": "UTIL", "titulo": "Falha simulada de conectividade",
     "analista": "Analista Demo 01", "pausas": []},
    {"numero": "900002", "contrato": "CLIENTE-A", "severidade": "Médio", "estado": "Fechado",
     "abertura": datetime(2026, 11, 16, 8), "fim": datetime(2026, 11, 19, 18),
     "meta_horas": 20, "calendario": "UTIL", "titulo": "Solicitação simulada de acesso",
     "analista": "Analista Demo 02", "pausas": [(datetime(2026, 11, 17, 12), datetime(2026, 11, 17, 14))]},
    {"numero": "900003", "contrato": "CLIENTE-B", "severidade": "Crítico", "estado": "Fechado",
     "abertura": datetime(2026, 11, 17, 9), "fim": datetime(2026, 11, 18, 12),
     "meta_horas": 72, "calendario": "CORRIDO", "titulo": "Alerta simulado de equipamento",
     "analista": "Analista Demo 03", "pausas": []},
    {"numero": "900004", "contrato": "CLIENTE-B", "severidade": "Alto", "estado": "Fechado",
     "abertura": datetime(2026, 11, 10, 8), "fim": datetime(2026, 11, 17, 8),
     "meta_horas": 120, "calendario": "CORRIDO", "titulo": "Instabilidade simulada de serviço",
     "analista": "Analista Demo 04", "pausas": []},
    {"numero": "900005", "contrato": "CLIENTE-C", "severidade": "Médio", "estado": "Aberto",
     "abertura": datetime(2026, 11, 18, 8), "fim": None,
     "meta_horas": 30, "calendario": "UTIL", "titulo": "Chamado fictício em acompanhamento",
     "analista": "Analista Demo 05", "pausas": []},
    {"numero": "900006", "contrato": "CLIENTE-B", "severidade": "Crítico", "estado": "Aberto",
     "abertura": datetime(2026, 11, 17, 0), "fim": None,
     "meta_horas": 72, "calendario": "CORRIDO", "titulo": "Incidente simulado próximo do limite",
     "analista": "Analista Demo 06", "pausas": []},
]


def gerar_registros(referencia=None):
    """Gera registros com dados fictícios e cálculos pelo mesmo motor do dashboard/chat."""
    referencia = referencia or datetime(2026, 11, 19, 15)
    saida = []
    for item in TICKETS:
        c = CalendarioSLA(horas_corridas=item["calendario"] == "CORRIDO")
        fim = item["fim"] or max(referencia, item["abertura"])
        consumido = calcular_tempo_liquido(item["abertura"], fim, c, item["pausas"])
        pct = percentual_consumido(consumido, timedelta(hours=item["meta_horas"]))
        situacao = ("Violado" if pct > 100 else "Dentro do SLA") if item["fim"] else "Em andamento"
        saida.append({**item, "tempo_horas": round(consumido.total_seconds() / 3600, 2),
                      "percentual": pct, "situacao_sla": situacao})
    return saida
