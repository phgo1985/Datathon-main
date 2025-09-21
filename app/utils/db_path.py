from pathlib import Path

def get_db_path():
    """
    Retorna o caminho absoluto do banco de dados, resolvendo a partir da raiz do projeto.
    Funciona em notebooks, scripts e ambientes colaborativos.
    """
    # Começa do diretório atual
    current = Path.cwd()

    # Sobe até encontrar a pasta 'datathon'
    while current.name != "datathon" and current != current.parent:
        current = current.parent

    # Monta o caminho do banco
    db_path = current / "app" / "data" / "extraidos" / "dados.db"

    if not db_path.exists():
        raise FileNotFoundError(f"Banco de dados não encontrado em: {db_path}")

    return str(db_path)