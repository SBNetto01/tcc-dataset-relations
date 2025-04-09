import pandas as pd

class AttributeValidator:
    """Classe que valida a similaridade entre atributos de diferentes datasets
    Utiliza heurísticas baseadas em nome, tipo e distribuição de dados pra sugerir compatibilidade"""

    def __init__(self, df1: pd.DataFrame, df2: pd.DataFrame):
        self.df1 = df1
        self.df2 = df2

    def compare_column_names(self):
        """Compara nomes de colunas para encontrar correspondências"""
        matches = []
        for col1 in self.df1.columns:
            for col2 in self.df2.columns:
                if col1.lower() == col2.lower():
                    matches.append((col1, col2, "match_exato"))
                elif col1.lower() in col2.lower() or col2.lower() in col1.lower():
                    matches.append((col1, col2, "possível_match"))
        return matches

    def compare_column_types(self):
        """Compara os tipos de dados das colunas com mesmo nome"""
        type_matches = []
        for col1 in self.df1.columns:
            for col2 in self.df2.columns:
                if col1.lower() == col2.lower():
                    dtype1 = self.df1[col1].dtype
                    dtype2 = self.df2[col2].dtype
                    if dtype1 == dtype2:
                        type_matches.append((col1, col2, str(dtype1)))
        return type_matches

    def suggest_similar_attributes(self):
        """Sugere pares de atributos potencialmente compatíveis com base em nome e tipo"""
        name_matches = self.compare_column_names()
        type_matches = self.compare_column_types()

        suggestions = []
        for name_match in name_matches:
            for type_match in type_matches:
                if name_match[0] == type_match[0] and name_match[1] == type_match[1]:
                    suggestions.append({
                        "Coluna Dataset 1": name_match[0],
                        "Coluna Dataset 2": name_match[1],
                        "Tipo": type_match[2],
                        "Tipo de Similaridade": name_match[2]
                    })
        return suggestions
