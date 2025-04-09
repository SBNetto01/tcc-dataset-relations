import pandas as pd
import re
from rapidfuzz import fuzz
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import csr_matrix
class AttributeValidator:
    """
    Classe responsável por validar a similaridade entre atributos de diferentes datasets.
    Utiliza heurísticas baseadas em nome, tipo e distribuição de dados para sugerir compatibilidades.
    """

    def __init__(self, df1: pd.DataFrame, df2: pd.DataFrame, fuzzy_threshold: int = 80, content_threshold: float = 0.5):
        self.df1 = df1
        self.df2 = df2
        self.fuzzy_threshold = fuzzy_threshold
        self.content_threshold = content_threshold

    def comparar_nomes_colunas(self):
        """Compara nomes de colunas para encontrar correspondências exatas ou semelhantes."""
        matches = []
        for col1 in self.df1.columns:
            for col2 in self.df2.columns:
                if col1.lower() == col2.lower():
                    matches.append((col1, col2, "match_exato"))
                elif col1.lower() in col2.lower() or col2.lower() in col1.lower():
                    matches.append((col1, col2, "possível_match"))
                else:
                    score = fuzz.token_sort_ratio(col1.lower(), col2.lower())
                    if score >= self.fuzzy_threshold:
                        matches.append((col1, col2, f"fuzzy_match ({score}%)"))
        return matches

    from scipy.sparse import csr_matrix  # Add this import

    def comparar_conteudo_colunas(self, serie1: pd.Series, serie2: pd.Series):
        """
        Compara os conteúdos de duas colunas usando similaridade de texto (cosine similarity)
        ou proximidade numérica para colunas numéricas.
        """
        # Verifica se ambas as colunas são numéricas
        if pd.api.types.is_numeric_dtype(serie1) and pd.api.types.is_numeric_dtype(serie2):
            # Calcula a interseção de valores únicos
            valores_comuns = set(serie1.dropna().unique()) & set(serie2.dropna().unique())
            total_valores = len(set(serie1.dropna().unique()) | set(serie2.dropna().unique()))
            if total_valores == 0:
                return 0.0
            return len(valores_comuns) / total_valores

        # Caso contrário, trata como texto
        
    def detectar_padrao(self, serie: pd.Series):
        """
        Detecta o padrão predominante em uma coluna usando expressões regulares.
        """
        patterns = {
            "email": r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
            "phone": r'\(?\d{2,3}\)?[-.\s]?\d{4,5}[-.\s]?\d{4}',
            "date": r'\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4}',
            "numeric": r'^\d+$',
            "cpf": r'^\d{3}\.\d{3}\.\d{3}-\d{2}$',
        }
    
        matches = {key: 0 for key in patterns.keys()}
    
        for value in serie.dropna():
            for key, pattern in patterns.items():
                if re.match(pattern, str(value)):
                    matches[key] += 1
    
        # Retorna o padrão com mais correspondências
        return max(matches, key=matches.get) if max(matches.values()) > 0 else "unknown"

    def comparar_tipos_colunas(self, serie1: pd.Series, serie2: pd.Series):
        """
        Compara os tipos de dados predominantes em duas colunas.
        """
        # Use self to call detectar_padrao
        padrao1 = self.detectar_padrao(serie1)
        padrao2 = self.detectar_padrao(serie2)

        return padrao1 == padrao2

    def comparar_atributos(self, col1: str, serie1: pd.Series, col2: str, serie2: pd.Series):
            """
            Compara dois atributos específicos e retorna a similaridade de nomes e conteúdos.
            """
            tipo1 = serie1.dtype
            tipo2 = serie2.dtype

            # Similaridade de nomes
            if col1.lower() == col2.lower():
                similaridade_nome = "match_exato"
            elif col1.lower() in col2.lower() or col2.lower() in col1.lower():
                similaridade_nome = "possível_match"
            else:
                score = fuzz.token_sort_ratio(col1.lower(), col2.lower())
                similaridade_nome = f"fuzzy_match ({score}%)" if score >= self.fuzzy_threshold else f"sem_match_suficiente ({score}%)"

            # Similaridade de conteúdos
            similaridade_conteudo = self.comparar_conteudo_colunas(serie1, serie2)

            return {
                "Coluna Dataset 1": col1,
                "Coluna Dataset 2": col2,
                "Tipo Dataset 1": str(tipo1),
                "Tipo Dataset 2": str(tipo2),
                "Similaridade de Nome": similaridade_nome,
                "Similaridade de Conteúdo": f"{similaridade_conteudo:.2f}"
            }

    def sugerir_atributos_similares(self):
        """Sugere pares de atributos potencialmente compatíveis com base em padrões de dados."""
        sugestoes = []
        for col1 in self.df1.columns:
            for col2 in self.df2.columns:
                # Use self to call detectar_padrao
                padrao1 = self.detectar_padrao(self.df1[col1])
                padrao2 = self.detectar_padrao(self.df2[col2])

                if padrao1 == padrao2 and padrao1 != "unknown":
                    sugestoes.append({
                        "Coluna Dataset 1": col1,
                        "Coluna Dataset 2": col2,
                        "Padrão Detectado": padrao1
                    })

        return sugestoes