import difflib #

class AttributeMatcher:
    def __init__(self):
        """
        Inicializa o AttributeMatcher.
        Não precisa mais armazenar DataFrames ou limiares globais aqui,
        pois os métodos serão mais focados.
        """
        pass

    def get_name_similarity(self, name1: str, name2: str) -> float:
        """
        Calcula a medida de similaridade percentual entre dois nomes de colunas.
        Utiliza difflib.SequenceMatcher. Retorna um valor entre 0 e 100.

        Args:
            name1 (str): Nome da primeira coluna.
            name2 (str): Nome da segunda coluna.

        Returns:
            float: Percentual de similaridade (0-100).
        """
        if not isinstance(name1, str) or not isinstance(name2, str):
            # Trata casos onde os nomes podem não ser strings.
            # Idealmente, os nomes das colunas são sempre strings.
            return 0.0
        
        # Converte para minúsculas para comparação case-insensitive
        str1_lower = name1.lower()
        str2_lower = name2.lower()
        
        # difflib.SequenceMatcher().ratio() retorna um valor entre 0 e 1.
        similarity_ratio = difflib.SequenceMatcher(None, str1_lower, str2_lower).ratio() #
        
        return similarity_ratio * 100 # Converte para porcentagem

# Os métodos _data_type_similarity, _value_distribution_similarity, e match_attributes
# podem ser removidos desta classe se ela for focada em ser um helper para o FKFinder.
# O FKFinder usará os tipos do DataProfiler e a lógica de inclusão é específica dele.
# Manter a classe mais simples e focada em fornecer a similaridade de nomes como
# sua principal contribuição para o FKFinder.