import pandas as pd
import os
import numpy as np

class DataProfiler:
    """
    Classe responsável por analisar datasets e extrair informações úteis para
    identificação de padrões, tipos de dados e possíveis chaves primárias.
    """
    def __init__(self, df: pd.DataFrame):
        self.df = df.replace(r'^\s*$', np.nan, regex=True) 

    def basic_statistics(self):
        """Retorna estatísticas básicas do dataset."""
        stats = {
            "Número de Linhas": int(self.df.shape[0]),
            "Número de Colunas": int(self.df.shape[1]),
            "Valores Nulos": self.df.isnull().sum().astype(int).to_dict(),
            "Tipos de Dados": self.df.dtypes.apply(lambda x: x.name).to_dict()
        }
        return stats

    def identify_primary_keys(self):
        """Tenta identificar possíveis chaves primárias com base em heurísticas aprimoradas."""
        candidate_keys = []

        for col in self.df.columns:
            if self.df[col].nunique(dropna=False) == len(self.df):
                if self.df[col].dtype in ["int64", "int32", "object", "string"]:
                    if 'id' in col.lower():
                        candidate_keys.insert(0, col)
                    else:
                        candidate_keys.append(col)

        return candidate_keys if candidate_keys else None

    def profile(self):
        """Gera um relatório consolidado do dataset."""
        return {
            "Estatísticas Básicas": self.basic_statistics(),
            "Possíveis Chaves Primárias": self.identify_primary_keys()
        }

if __name__ == "__main__":
    df = pd.DataFrame({
        'ID': [1, 2, '', '', 5],
        'Nome': ['Ana', 'Bruno', 'Carlos', '', 'Eduardo'],  
        'Idade': [25, 30, '', 28, 35],                       
        'Salário': [3000, 4000, 2500, '', 5000]              
    })
    profiler = DataProfiler(df)
    print(profiler.profile())