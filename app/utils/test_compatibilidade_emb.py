import unittest
from compatibilidade_emb import calcular_compatibilidade_emb

class TestCompatibilidadeEmb(unittest.TestCase):

    def test_estrutura_do_retorno(self):
        requisitos = "Python\nMachine Learning\nSQL"
        experiencia = "Tenho experiência com Python e Machine Learning."
        resultado = calcular_compatibilidade_emb(requisitos, experiencia)

        self.assertIsInstance(resultado, dict)
        self.assertIn("score", resultado)
        self.assertIn("mais_compativeis", resultado)
        self.assertIn("menos_compativeis", resultado)

    def test_mais_e_menos_compativeis(self):
        requisitos = "Python\nMachine Learning\nSQL"
        experiencia = "Trabalho com Python e Machine Learning diariamente."
        resultado = calcular_compatibilidade_emb(requisitos, experiencia)

        self.assertIn("Python", resultado["mais_compativeis"])
        self.assertIn("Machine Learning", resultado["mais_compativeis"])
        self.assertIn("SQL", resultado["menos_compativeis"])

    def test_requisitos_vazios(self):
        requisitos = ""
        experiencia = "Tenho experiência com Python."
        resultado = calcular_compatibilidade_emb(requisitos, experiencia)
        self.assertEqual(resultado["score"], 0)
        self.assertEqual(resultado["mais_compativeis"], [])
        self.assertEqual(resultado["menos_compativeis"], [])

    def test_experiencia_vazia(self):
        requisitos = "Python\nSQL"
        experiencia = ""
        resultado = calcular_compatibilidade_emb(requisitos, experiencia)
        self.assertTrue(resultado["score"] < 10)
        self.assertEqual(len(resultado["mais_compativeis"]), 0)

if __name__ == '__main__':
    unittest.main()
