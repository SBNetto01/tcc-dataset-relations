import pandas as pd
import numpy as np
import difflib
from typing import List, Tuple, Dict


class AttributeMatcher:

    def __init__(self, df1: pd.DataFrame, df2: pd.DataFrame):
        self.df1 = df1
        self.df2 = df2

    def _string_similarity(self, str1: str, str2: str) -> float:
        """Retorna medida de similaridade entre dois nomes de colunas. Utiliza SequenceMatcher (Levenshtein simplificado)."""
        return difflib.SequenceMatcher(None, str1.lower(), str2.lower()).ratio()

    def _data_type_similarity(self, col1: pd.Series, col2: pd.Series) -> bool:
        """Verifica os tipos"""
        return col1.dtype == col2.dtype

    def _value_distribution_similarity(self, col1: pd.Series, col2: pd.Series, threshold: float = 0.6) -> bool:
        """Compara a distribuição de valores únicos entre duas colunas. Retorna True se a sobreposição for acima do threshold."""
        set1 = set(col1.dropna().unique())
        set2 = set(col2.dropna().unique())

        if not set1 or not set2:
            return False

        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        similarity = intersection / union

        return similarity >= threshold

    def match_attributes(self, name_threshold: float = 0.8) -> List[Dict[str, str]]:
        """Compara atributos entre os dois datasets e retorna pares similares."""
        matches = []

        for col1 in self.df1.columns:
            for col2 in self.df2.columns:
                name_sim = self._string_similarity(col1, col2)
                type_sim = self._data_type_similarity(self.df1[col1], self.df2[col2])
                dist_sim = self._value_distribution_similarity(self.df1[col1], self.df2[col2])

                if name_sim >= name_threshold or (type_sim and dist_sim):
                    matches.append({
                        "Coluna Dataset 1": col1,
                        "Coluna Dataset 2": col2,
                        "Similaridade de Nome": round(name_sim, 2),
                        "Tipos Compatíveis": type_sim,
                        "Distribuição Semelhante": dist_sim
                    })

        return matches
