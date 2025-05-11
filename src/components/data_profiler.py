import pandas as pd

class DataProfiler:
    def __init__(self, dataframe: pd.DataFrame):
        self.df = dataframe

    def generate_profile(self):
        profile = {
            "Estatísticas Básicas": self.basic_stats(),
            "Possíveis Chaves Primárias": self.possible_primary_keys()
        }
        return profile

    def basic_stats(self):
        return {
            "Número de Linhas": len(self.df),
            "Número de Colunas": len(self.df.columns),
            "Valores Nulos": self.df.isnull().sum().to_dict(),
            "Tipos de Dados": self.df.dtypes.astype(str).to_dict()
        }

    def possible_primary_keys(self):
        candidates = []
        for column in self.df.columns:
            if self.df[column].is_unique and not self.df[column].isnull().any():
                candidates.append(column)
        return candidates
