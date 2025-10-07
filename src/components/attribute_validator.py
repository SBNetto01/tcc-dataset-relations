import pandas as pd
from rapidfuzz import fuzz

class AttributeValidator:
    def __init__(self, df1: pd.DataFrame, df2: pd.DataFrame, fuzzy_threshold: int = 70):
        self.df1 = df1
        self.df2 = df2
        self.fuzzy_threshold = fuzzy_threshold

    def compare_column_names(self):
        matches = []
        for col1 in self.df1.columns:
            for col2 in self.df2.columns:
                score = fuzz.token_sort_ratio(col1.lower(), col2.lower())
                if score >= self.fuzzy_threshold:
                    matches.append((col1, col2, score))
        return matches

    def suggest_similar_attributes(self):
        name_matches = self.compare_column_names()
        suggestions = []

        for col1, col2, score in name_matches:
            dtype1 = self.df1[col1].dtype
            dtype2 = self.df2[col2].dtype

            if dtype1 == dtype2:
                suggestions.append({
                    "Coluna Dataset 1": col1,
                    "Coluna Dataset 2": col2,
                    "Tipo": str(dtype1),
                    "Porcentagem de Similaridade": f"{score:.4f}"
                })

        # Ordena as sugestões por score (decrescente)
        return sorted(suggestions, key=lambda x: float(x["Porcentagem de Similaridade"]), reverse=True)
