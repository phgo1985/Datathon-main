import os, json, sqlite3, zipfile
import pandas as pd
from os.path import splitext, basename
from utils.flatten_json import flatten_json

def validar_pasta(pasta_zips):
    return pasta_zips and os.path.isdir(pasta_zips)

def extrair_zip(zip_path, destino):
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(destino)
            return zip_ref.namelist()
    except zipfile.BadZipFile:
        print(f"ZIP inválido: {zip_path}")
        return []

def processar_json(caminho_arquivo, nome_tabela):
    with open(caminho_arquivo, encoding='utf-8') as f:
        dados = json.load(f)

    if nome_tabela == 'prospects':
        return transformar_prospects(dados)
    else:
        return transformar_generico(dados)

def transformar_prospects(dados):
    linhas = []
    for codigo_vaga, info_vaga in dados.items():
        vaga_info = {k: v for k, v in info_vaga.items() if k != "prospects"}
        vaga_info["codigo_vaga"] = codigo_vaga
        for prospect in info_vaga.get("prospects", []):
            linha = vaga_info.copy()
            for chave, valor in prospect.items():
                if chave in ["data_candidatura", "ultima_atualizacao"]:
                    valor = valor.replace("-", "/")
                linha[chave] = valor
            linhas.append(linha)
    df = pd.DataFrame(linhas)
    colunas_ordenadas = sorted(df.columns, key=lambda x: (x != "codigo_vaga", x))
    return df[colunas_ordenadas]

def transformar_generico(dados):
    registros = []
    if isinstance(dados, dict):
        for codigo, conteudo in dados.items():
            registro = flatten_json(conteudo)
            registro = {"codigo": codigo, **registro}
            registros.append(registro)
    return pd.DataFrame(registros)