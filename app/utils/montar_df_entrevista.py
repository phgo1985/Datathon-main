import sqlite3
import pandas as pd
from pathlib import Path
import os

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # sobe de utils para app
db_path = os.path.join(base_dir, 'data', 'extraidos', 'dados.db')

# Funções auxiliares
def montar_df_entrevista(email_candidato):
    """Busca o candidato por e-mail e faz join com prospects e vagas."""
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Banco de dados não encontrado em: {db_path}")

    conn = sqlite3.connect(db_path)
    df_applicants = pd.read_sql_query(
        "SELECT * FROM applicants WHERE LOWER(infos_basicas_email) LIKE ?",
        conn, params=(email_candidato.lower(),)
    )
    if df_applicants.empty:
        conn.close()
        return None
    df_prospects = pd.read_sql_query("SELECT * FROM prospects", conn)
    df_vagas = pd.read_sql_query("SELECT * FROM vagas", conn)
    conn.close()
    df_merged = df_applicants.merge(df_prospects, on="codigo", how="left")
    df_merged = df_merged.merge(df_vagas, left_on="codigo_vaga", right_on="codigo", how="left", suffixes=('', '_vaga'))
    return df_merged