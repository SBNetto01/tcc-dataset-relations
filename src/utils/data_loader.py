import pandas as pd
import sqlite3
from logger import log_info, log_error

def _load_dataframe(load_func, file_path, *args, **kwargs):
    """ auxiliar pra carregar DF e tratar erro """
    try:
        df = load_func(file_path, *args, **kwargs)
        print(f"✅ Dados carregados: {file_path} ({df.shape[0]} linhas, {df.shape[1]} colunas)")
        return df
    except FileNotFoundError:
        print(f"Erro: Arquivo não encontrado - {file_path}")
    except pd.errors.ParserError:
        print(f"Erro: Falha ao processar o arquivo - {file_path}")
    except Exception as e:
        print(f"Erro inesperado ao carregar {file_path}: {e}")
    return None

def load_csv(file_path, encoding='utf-8'):
    return _load_dataframe(pd.read_csv, file_path, encoding=encoding)

def load_json(file_path):
    return _load_dataframe(pd.read_json, file_path, orient='records')

def load_sql(db_path, query):
    """Executa uma consulta SQL e retorna um DF do pandas."""
    try:
        with sqlite3.connect(db_path) as conn:
            df = pd.read_sql_query(query, conn)
            print(f"✅ Dados carregados do banco: {db_path} ({df.shape[0]} linhas, {df.shape[1]} colunas)")
            return df
    except sqlite3.DatabaseError as e:
        print(f"Erro no banco de dados: {e}")
    except Exception as e:
        print(f"Erro inesperado ao executar SQL: {e}")
    return None

#função pra log
def load_csv(file_path):
    try:
        df = pd.read_csv(file_path)
        log_info(f"CSV carregado: {file_path} ({df.shape[0]} linhas, {df.shape[1]} colunas)")
        return df
    except Exception as e:
        log_error(f"Erro ao carregar CSV: {e}")
        return None

