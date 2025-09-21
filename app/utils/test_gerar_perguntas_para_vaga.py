import unittest
from unittest.mock import patch, MagicMock
from gerar_perguntas_para_vaga import gerar_perguntas_para_vaga


class TestGerarPerguntasParaVaga(unittest.TestCase):

    @patch("gerar_perguntas_para_vaga.ChatOpenAI")
    @patch("gerar_perguntas_para_vaga.LLMChain")
    def test_gerar_perguntas_mockado(self, mock_llmchain, mock_chatopenai):
        mock_chain_instance = MagicMock()
        mock_chain_instance.run.return_value = """Quais são suas principais habilidades técnicas?
Como você aplica essas competências no dia a dia?
Você possui certificações relevantes para esta área?
Como você lida com desafios em equipe?
Qual sua experiência com projetos na área de atuação?"""
        mock_llmchain.return_value = mock_chain_instance

        linha = {
            "informacoes_pessoais_nome": "João Silva",
            "informacoes_profissionais_area_atuacao": "Desenvolvimento de Software",
            "informacoes_profissionais_conhecimentos_tecnicos": "Python, Django, REST",
            "informacoes_profissionais_certificacoes": "AWS Certified Developer",
            "informacoes_profissionais_nivel_profissional": "Pleno",
            "formacao_e_idiomas_nivel_academico": "Superior Completo",
            "formacao_e_idiomas_nivel_ingles": "Avançado",
            "formacao_e_idiomas_nivel_espanhol": "Intermediário",
            "informacoes_basicas_titulo_vaga": "Desenvolvedor Backend",
            "informacoes_basicas_objetivo_vaga": "Desenvolver APIs escaláveis",
            "perfil_vaga_competencia_tecnicas_e_comportamentais": "Conhecimento em Python e boas práticas de desenvolvimento",
            "perfil_vaga_habilidades_comportamentais_necessarias": "Trabalho em equipe, comunicação clara"
        }

        perguntas, resumo, competencias, titulo, objetivo = gerar_perguntas_para_vaga(linha)

        self.assertEqual(len(perguntas), 5)
        self.assertIn("Quais são suas principais habilidades técnicas?", perguntas)
        self.assertEqual(titulo, "Desenvolvedor Backend")
        self.assertEqual(objetivo, "Desenvolver APIs escaláveis")
        self.assertIn("João Silva", resumo)
        self.assertIn("Python", competencias)

if __name__ == '__main__':
    unittest.main()
