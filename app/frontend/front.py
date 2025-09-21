import streamlit as st
import requests
import os
from dotenv import load_dotenv

load_dotenv()
API_URL = os.getenv("API_URL", "http://localhost:5000")

st.title("Entrevista RH - Candidato")

# Inicializar variáveis de estado
if "email" not in st.session_state:
    st.session_state.email = ""
if "fase" not in st.session_state:
    st.session_state.fase = "inicio"
if "dados_vaga" not in st.session_state:
    st.session_state.dados_vaga = {}
if "perguntas" not in st.session_state:
    st.session_state.perguntas = []
if "respostas" not in st.session_state:
    st.session_state.respostas = []

# Fase 1: entrada do email
if st.session_state.fase == "inicio":
    email = st.text_input("Digite seu e-mail para iniciar a entrevista:")
    if st.button("Iniciar entrevista") and email:
        response = requests.post(f"{API_URL}/iniciar-entrevista", json={"email": email})
        data = response.json()

        if response.status_code != 200:
            st.error(data.get("erro", "Erro ao iniciar entrevista"))
        else:
            st.session_state.email = email
            if data["status"] == "escolha_vaga":
                st.session_state.fase = "escolha_vaga"
                st.session_state.vagas_disponiveis = data["vagas"]
                st.session_state.nome = data["nome"]
            elif data["status"] == "ok":
                st.session_state.fase = "entrevista"
                st.session_state.dados_vaga = data
                st.session_state.perguntas = data["perguntas"]

# Fase 2: seleção de vaga
if st.session_state.fase == "escolha_vaga":
    st.subheader(f"Olá, {st.session_state.nome}! Escolha a vaga para entrevista:")
    vaga_opcao = st.selectbox("Vagas disponíveis", options=st.session_state.vagas_disponiveis, format_func=lambda x: x["titulo_vaga"])
    if st.button("Selecionar vaga"):
        indice = vaga_opcao["indice"]
        response = requests.post(f"{API_URL}/gerar-perguntas", json={"email": st.session_state.email, "indice_vaga": indice})
        data = response.json()
        if response.status_code == 200:
            st.session_state.fase = "entrevista"
            st.session_state.dados_vaga = data
            st.session_state.perguntas = data["perguntas"]
            st.session_state.indice_vaga = indice
        else:
            st.error(data.get("erro", "Erro ao gerar perguntas"))

# Fase 3: entrevista
if st.session_state.fase == "entrevista":
    dados = st.session_state.dados_vaga
    st.subheader(f"Entrevista para: {dados['titulo_vaga']}")
    st.write(f"🎯 Objetivo da vaga: {dados['objetivo_vaga']}")
    st.write(f"🧠 Competências esperadas: {dados['competencias']}")
    st.write(f"📄 Resumo da vaga: {dados['resumo']}")

    respostas = []
    for i, pergunta in enumerate(st.session_state.perguntas):
        resposta = st.text_area(f"{i+1}. {pergunta}", key=f"resposta_{i}")
        respostas.append(resposta)

    if st.button("Enviar respostas"):
        payload = {
            "email": st.session_state.email,
            "indice_vaga": st.session_state.get("indice_vaga", 0),
            "perguntas": st.session_state.perguntas,
            "respostas": respostas
        }
        response = requests.post(f"{API_URL}/avaliar-entrevista", json=payload)
        resultado = response.json()

        if response.status_code == 200:
            st.success(f"✅ Resultado: {resultado['resultado']}")
            st.metric("Score compatibilidade semântica", resultado["score_compatibilidade_semantica"])
            st.metric("Score compatibilidade vetorial", resultado["score_compatibilidade_vetorial"])
            st.write("✅ Requisitos mais compatíveis:")
            st.write(resultado["requisitos_mais_compatíveis"])
            st.write("⚠️ Requisitos menos compatíveis:")
            st.write(resultado["requisitos_menos_compatíveis"])
            st.write("🔍 Requisitos vetoriais relevantes:")
            st.write(resultado["requisitos_vetoriais_relevantes"])
        else:
            st.error(resultado.get("erro", "Erro ao avaliar entrevista"))