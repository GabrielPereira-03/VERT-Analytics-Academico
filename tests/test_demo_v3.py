import unittest
from datetime import date

from demo_v3.data import gerar_registros
from demo_v3.reports import excel, filtrar, pdf, resumo


class TestRelatoriosDemo(unittest.TestCase):
    def setUp(self):
        self.todos = gerar_registros()
        self.inicio, self.fim = date(2026, 11, 1), date(2026, 11, 30)

    def test_total_e_situacoes(self):
        k = resumo(self.todos)
        self.assertEqual((k["total"], k["fechados"], k["abertos"]), (6, 4, 2))
        self.assertEqual(k["violados"], 2)
        self.assertEqual(k["dentro"], 2)
        self.assertEqual(k["cumprimento"], 50.0)

    def test_novo_exemplo_em_risco(self):
        r = next(r for r in self.todos if r["numero"] == "900006")
        self.assertIsNone(r["fim"])
        self.assertTrue(75 <= r["percentual"] <= 100)

    def test_filtro_contrato(self):
        cet = filtrar(self.todos, "CLIENTE-A", self.inicio, self.fim)
        self.assertEqual(len(cet), 2)
        self.assertTrue(all(r["contrato"] == "CLIENTE-A" for r in cet))

    def test_excel_valido(self):
        buf = excel(self.todos, "TODOS", self.inicio, self.fim)
        self.assertTrue(buf.startswith(b"PK"))

    def test_pdf_valido(self):
        buf = pdf(self.todos, "TODOS", self.inicio, self.fim)
        self.assertTrue(buf.startswith(b"%PDF"))

    def test_filtro_invertido(self):
        with self.assertRaises(ValueError):
            filtrar(self.todos, "TODOS", self.fim, self.inicio)


if __name__ == "__main__":
    unittest.main()
