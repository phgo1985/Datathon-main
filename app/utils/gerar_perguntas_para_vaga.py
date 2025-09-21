from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain

def gerar_perguntas_para_vaga(linha):
    nome = linha.get("informacoes_pessoais_nome", "")
    area = linha.get("informacoes_profissionais_area_atuacao", "")
    tecnicos = linha.get("informacoes_profissionais_conhecimentos_tecnicos", "")
    certificacoes = linha.get("informacoes_profissionais_certificacoes", "")
    nivel_prof = linha.get("informacoes_profissionais_nivel_profissional", "")
    nivel_acad = linha.get("formacao_e_idiomas_nivel_academico", "")
    ingles = linha.get("formacao_e_idiomas_nivel_ingles", "")
    espanhol = linha.get("formacao_e_idiomas_nivel_espanhol", "")

    titulo_vaga = linha.get("informacoes_basicas_titulo_vaga", "") or ""
    objetivo_vaga = linha.get("informacoes_basicas_objetivo_vaga", "") or ""
    comp_tec = linha.get("perfil_vaga_competencia_tecnicas_e_comportamentais", "") or ""
    comp_comp = linha.get("perfil_vaga_habilidades_comportamentais_necessarias", "") or ""

    resumo = (
        f"Nome: {nome}\n"
        f"Área de atuação: {area}\n"
        f"Conhecimentos técnicos: {tecnicos}\n"
        f"Certificações: {certificacoes}\n"
        f"Nível profissional: {nivel_prof}\n"
        f"Nível acadêmico: {nivel_acad}\n"
        f"Inglês: {ingles}, Espanhol: {espanhol}"
    )
    competencias = f"{comp_tec}\n{comp_comp}".strip()

    prompt = ChatPromptTemplate.from_template("""
Você é um agente de RH entrevistando um candidato para a vaga de "{titulo_vaga}".
Objetivo da vaga: {objetivo_vaga}
Perfil do candidato:
{resumo}

Competências exigidas:
{competencias}

Gere 5 perguntas para avaliar se o candidato possui as competências necessárias.
Seja direto e profissional.
Cada pergunta em uma linha, sem numeração e sem texto extra.
""")

    llm = ChatOpenAI(temperature=0.7)
    chain = LLMChain(llm=llm, prompt=prompt)
    perguntas_texto = chain.run({
        "titulo_vaga": titulo_vaga,
        "objetivo_vaga": objetivo_vaga,
        "resumo": resumo,
        "competencias": competencias
    })

    perguntas = [p.strip("-• ").strip() for p in perguntas_texto.split("\n") if p.strip()]
    if len(perguntas) > 5:
        perguntas = perguntas[:5]
    return perguntas, resumo, competencias, titulo_vaga, objetivo_vaga