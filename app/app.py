from flask import Flask, jsonify, request, render_template
from pathlib import Path
from os.path import join, basename, splitext
import pandas as pd
import os
from datetime import timedelta, datetime
import zipfile
import sqlite3
import json

import mlflow
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from dotenv import load_dotenv

from utils.montar_df_entrevista import montar_df_entrevista
from utils.semantic_engine import criar_vector_store, buscar_similaridade
from utils.calcular_compatibilidade_emb import calcular_compatibilidade_emb
from utils.gerar_perguntas_para_vaga import gerar_perguntas_para_vaga
from utils.etl_zip import validar_pasta, extrair_zip, processar_json

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return jsonify({'mensagem': 'API pronta para processar diversos ZIPs!'})

@app.route('/processar_todos_zips', methods=['POST'])
def processar_todos_zips():
    data = request.get_json()
    pasta_zips = data.get('pasta_zips')
    destino = data.get('destino')
    db_path = data.get('db_path', 'dados.db')

    if not validar_pasta(pasta_zips):
        return jsonify({'erro': 'Pasta de ZIPs inválida ou inexistente.'}), 400

    os.makedirs(destino, exist_ok=True)
    conn = sqlite3.connect(db_path)
    tabelas_criadas = []
    arquivos_processados = []

    for nome_arquivo in os.listdir(pasta_zips):
        if nome_arquivo.endswith(".zip"):
            zip_path = os.path.join(pasta_zips, nome_arquivo)
            arquivos_extraidos = extrair_zip(zip_path, destino)
            if arquivos_extraidos:
                arquivos_processados.append(nome_arquivo)

            for arquivo in arquivos_extraidos:
                if arquivo.endswith(".json"):
                    caminho_arquivo = os.path.join(destino, arquivo)
                    if os.path.isfile(caminho_arquivo):
                        nome_tabela = splitext(basename(arquivo))[0]
                        df = processar_json(caminho_arquivo, nome_tabela)
                        if df is not None:
                            df.to_sql(nome_tabela, conn, if_exists='replace', index=False)
                            tabelas_criadas.append(nome_tabela)
                            print(f"Tabela '{nome_tabela}' salva com sucesso.")
                        else:
                            print(f"Estrutura não reconhecida em '{arquivo}', tabela não criada.")

    conn.close()

    return jsonify({
        'mensagem': f'Todos os ZIPs foram processados.',
        'tabelas_salvas': tabelas_criadas,
        'banco': db_path,
        'zips_processados': arquivos_processados
    })

@app.route('/consultar/<tabela>', methods=['GET'])
def consultar_tabela(tabela):
    try:
        # Caminho absoluto baseado no local do script
        base_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(base_dir, 'data', 'extraidos', 'dados.db')

        conn = sqlite3.connect(db_path)
        df = pd.read_sql_query(f"SELECT * FROM {tabela} LIMIT 50", conn)
        conn.close()
        return jsonify(df.to_dict(orient='records'))
    except Exception as e:
        return jsonify({'erro': f'Erro ao consultar a tabela: {str(e)}'}), 400

@app.route("/iniciar-entrevista", methods=["POST"])
def iniciar_entrevista():
    email = (request.json.get("email") or "").strip().lower()
    df_merged = montar_df_entrevista(email)
    if df_merged is None:
        return jsonify({"erro": "Candidato não encontrado"}), 404

    nome = df_merged.iloc[0].get("informacoes_pessoais_nome", "")
    if len(df_merged) > 1:
        vagas = [{"indice": int(i), "titulo_vaga": row.get("informacoes_basicas_titulo_vaga", "")}
                 for i, row in df_merged.iterrows()]
        return jsonify({"status": "escolha_vaga", "nome": nome, "vagas": vagas})

    perguntas, resumo, competencias, titulo_vaga, objetivo_vaga = gerar_perguntas_para_vaga(df_merged.iloc[0])
    return jsonify({
        "status": "ok",
        "nome": nome,
        "titulo_vaga": titulo_vaga,
        "objetivo_vaga": objetivo_vaga,
        "competencias": competencias,
        "resumo": resumo,
        "perguntas": perguntas
    })

@app.route("/gerar-perguntas", methods=["POST"])
def gerar_perguntas_vaga():
    dados = request.get_json()
    email = (dados.get("email") or "").strip().lower()
    indice_vaga = dados.get("indice_vaga")

    if email == "" or indice_vaga is None:
        return jsonify({"erro": "email e indice_vaga são obrigatórios"}), 400

    df_merged = montar_df_entrevista(email)
    if df_merged is None or df_merged.empty:
        return jsonify({"erro": "Candidato não encontrado"}), 404

    try:
        linha = df_merged.iloc[int(indice_vaga)]
    except Exception:
        return jsonify({"erro": "indice_vaga inválido"}), 400

    perguntas, resumo, competencias, titulo_vaga, objetivo_vaga = gerar_perguntas_para_vaga(linha)

    return jsonify({
        "status": "ok",
        "nome": linha.get("informacoes_pessoais_nome", ""),
        "titulo_vaga": titulo_vaga,
        "objetivo_vaga": objetivo_vaga,
        "competencias": competencias,
        "resumo": resumo,
        "perguntas": perguntas
    })

@app.route("/avaliar-entrevista", methods=["POST"])
def avaliar_entrevista():
    dados = request.json
    email = (dados.get("email") or "").strip().lower()
    indice_vaga = dados.get("indice_vaga", 0)
    perguntas = dados.get("perguntas", [])
    respostas = dados.get("respostas", [])

    df_merged = montar_df_entrevista(email)
    if df_merged is None:
        return jsonify({"erro": "Candidato não encontrado"}), 404

    linha = df_merged.iloc[int(indice_vaga)]
    nome = linha.get("informacoes_pessoais_nome", "")
    titulo_vaga = linha.get("informacoes_basicas_titulo_vaga", "")
    objetivo_vaga = linha.get("informacoes_basicas_objetivo_vaga", "")
    requisitos = linha.get("perfil_vaga_competencia_tecnicas_e_comportamentais", "")
    comp_comp = linha.get("perfil_vaga_habilidades_comportamentais_necessarias", "")
    competencias_full = f"{requisitos}\n{comp_comp}".strip()
    experiencia = linha.get("informacoes_profissionais_conhecimentos_tecnicos", "")
    respostas_texto = "\n".join(respostas)
    cv_resumo = linha.get("cv_pt", "")
    experiencia_completa = f"{experiencia}\n{cv_resumo}\n{respostas_texto}".strip()
    
    # 1. Compatibilidade semântica direta
    resultado_detalhado = calcular_compatibilidade_emb(requisitos, experiencia_completa)
    score_emb = resultado_detalhado["score"]
    mais_compativeis = resultado_detalhado["mais_compativeis"]
    menos_compativeis = resultado_detalhado["menos_compativeis"]

    # 2. Compatibilidade vetorial via FAISS
    requisitos_texto = requisitos if requisitos else ""
    comportamentais_texto = comp_comp if comp_comp else ""

    requisitos_lista = [
        r.strip()
        for r in requisitos_texto.split("\n") + comportamentais_texto.split("\n")
        if r.strip()]

    vector_store = criar_vector_store(requisitos_lista)
    resultados_vetoriais = buscar_similaridade(experiencia_completa, vector_store, k=5)

    requisitos_vetoriais = [r.page_content for r in resultados_vetoriais if r.page_content not in menos_compativeis]

    score_vetorial = round(len(requisitos_vetoriais) / len(requisitos_lista) * 100, 2) if requisitos_lista else 0

    # 3. Decisão final
    resultado = "APTO" if score_emb > 10 and score_vetorial > 50 else "NÃO APTO"

    # 4. Log no MLflow
    with mlflow.start_run(run_name=f"Entrevista_{nome}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"):
        mlflow.log_param("nome", nome)
        mlflow.log_param("email", email)
        mlflow.log_param("vaga", titulo_vaga)
        mlflow.log_param("objetivo_vaga", objetivo_vaga)
        mlflow.log_param("resultado", resultado)
        mlflow.log_param("competencias", competencias_full)
        mlflow.log_metric("compatibilidade_tecnica", score_emb)
        mlflow.log_metric("score_vetorial", score_vetorial)
        mlflow.log_text("\n".join(perguntas), "perguntas_geradas.txt")
        mlflow.log_text("\n".join([f"Q: {q}\nA: {r}" for q, r in zip(perguntas, respostas)]), "respostas_candidato.txt")
        mlflow.log_text(respostas_texto, "respostas_processadas.txt")
        mlflow.log_text(cv_resumo, "cv_resumo.txt")

    # 5. Retorno final

    return jsonify({
        "status": "ok",
        "nome": nome,
        "titulo_vaga": titulo_vaga,
        "resultado": resultado,
        "score_compatibilidade_semantica": score_emb,
        "score_compatibilidade_vetorial": score_vetorial,
        "requisitos_mais_compatíveis": mais_compativeis,
        "requisitos_menos_compatíveis": menos_compativeis,
        "requisitos_vetoriais_relevantes": requisitos_vetoriais
    })

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)