import unittest
from datetime import date, datetime, time, timedelta

from sla_core.engine import (
    CalendarioSLA, calcular_tempo_liquido, mesclar_intervalos,
    percentual_consumido, projetar_vencimento,
)


class TestMotorSLA(unittest.TestCase):
    def setUp(self):
        self.comercial = CalendarioSLA()
        self.corrido = CalendarioSLA(horas_corridas=True)

    def test_horas_corridas_entre_dias(self):
        inicio = datetime(2026, 11, 19, 22)
        fim = datetime(2026, 11, 20, 2)
        self.assertEqual(calcular_tempo_liquido(inicio, fim, self.corrido), timedelta(hours=4))

    def test_fim_de_semana_e_expediente(self):
        sexta = datetime(2026, 11, 20, 17)
        segunda = datetime(2026, 11, 23, 10)
        self.assertEqual(calcular_tempo_liquido(sexta, segunda, self.comercial), timedelta(hours=3))

    def test_feriado(self):
        cal = CalendarioSLA(feriados=frozenset({date(2026, 11, 20)}))
        ini = datetime(2026, 11, 19, 17)
        fim = datetime(2026, 11, 23, 10)
        self.assertEqual(calcular_tempo_liquido(ini, fim, cal), timedelta(hours=3))

    def test_pausas_sobrepostas_nao_duplicam(self):
        ini, fim = datetime(2026, 11, 19, 8), datetime(2026, 11, 19, 18)
        pausas = [(datetime(2026, 11, 19, 10), datetime(2026, 11, 19, 12)),
                  (datetime(2026, 11, 19, 11), datetime(2026, 11, 19, 14))]
        self.assertEqual(calcular_tempo_liquido(ini, fim, self.comercial, pausas), timedelta(hours=6))
        self.assertEqual(len(mesclar_intervalos(pausas)), 1)

    def test_pausa_fora_do_intervalo(self):
        ini = datetime(2026, 11, 19, 8)
        fim = datetime(2026, 11, 19, 10)
        pausa = [(datetime(2026, 11, 20, 8), datetime(2026, 11, 20, 9))]
        self.assertEqual(calcular_tempo_liquido(ini, fim, self.comercial, pausa), timedelta(hours=2))

    def test_projecao_comercial_e_marco(self):
        ini = datetime(2026, 11, 20, 17)
        fim = projetar_vencimento(ini, timedelta(hours=3), self.comercial)
        self.assertEqual(fim, datetime(2026, 11, 23, 10))
        self.assertEqual(percentual_consumido(timedelta(hours=3), timedelta(hours=4)), 75.0)

    def test_projecao_com_pausa(self):
        ini = datetime(2026, 11, 19, 8)
        pausa = [(datetime(2026, 11, 19, 9), datetime(2026, 11, 19, 10))]
        self.assertEqual(projetar_vencimento(ini, timedelta(hours=3), self.comercial, pausa),
                         datetime(2026, 11, 19, 12))

    def test_intervalo_invalido(self):
        with self.assertRaises(ValueError):
            calcular_tempo_liquido(datetime(2026, 11, 20), datetime(2026, 11, 19), self.comercial)

    def test_meta_zero(self):
        with self.assertRaises(ValueError):
            percentual_consumido(timedelta(), timedelta())

    def test_sem_dias_uteis(self):
        cal = CalendarioSLA(dias_uteis=frozenset())
        with self.assertRaises(ValueError):
            projetar_vencimento(datetime(2026, 11, 19, 8), timedelta(hours=1), cal, limite_dias=5)


if __name__ == "__main__":
    unittest.main()
