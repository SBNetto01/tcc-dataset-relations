import pandas as pd

class DataProfiler:
    def __init__(self, dataframe: pd.DataFrame, 
                 pk_uniqueness_threshold: float = 99.0, 
                 pk_non_null_threshold: float = 99.0):
        """
        Inicializa o DataProfiler.

        Args:
            dataframe (pd.DataFrame): O DataFrame a ser perfilado.
            pk_uniqueness_threshold (float): Limiar de porcentagem de unicidade 
                                             para uma coluna ser considerada candidata a PK.
            pk_non_null_threshold (float): Limiar de porcentagem de não nulos 
                                           para uma coluna ser considerada candidata a PK.
        """
        self.df = dataframe
        self.pk_uniqueness_threshold = pk_uniqueness_threshold
        self.pk_non_null_threshold = pk_non_null_threshold

    def generate_profile(self):
        """
        Gera um perfil completo do DataFrame.
        """
        profile = {
            "Estatísticas Gerais": self.general_stats(), # Renomeado de "Estatísticas Básicas"
            "Perfil Detalhado das Colunas": self.column_details(), # Novo método para detalhar cada coluna
            "Candidatas a Chave Primária": self.identify_primary_key_candidates() # Renomeado e modificado
        }
        return profile

    def general_stats(self):
        """
        Calcula estatísticas gerais do DataFrame.
        """
        return {
            "Número de Linhas": len(self.df),
            "Número de Colunas": len(self.df.columns),
            "Total de Valores Nulos no DataFrame": self.df.isnull().sum().sum(), # Soma total de nulos
            "Tipos de Dados das Colunas": self.df.dtypes.astype(str).to_dict()
        }

    def column_details(self):
        """
        Gera um perfil detalhado para cada coluna.
        """
        details = []
        for column_name in self.df.columns:
            column_data = self.df[column_name]
            num_total = len(column_data)
            num_null = column_data.isnull().sum()
            non_null_percentage = ((num_total - num_null) / num_total) * 100 if num_total > 0 else 0
            num_unique = column_data.nunique()
            uniqueness_score = (num_unique / num_total) * 100 if num_total > 0 else 0
            
            details.append({
                "Nome da Coluna": column_name,
                "Tipo de Dado": str(column_data.dtype),
                "Valores Nulos": int(num_null),
                "Porcentagem de Não Nulos": round(non_null_percentage, 2),
                "Valores Únicos": int(num_unique),
                "Porcentagem de Unicidade": round(uniqueness_score, 2),
                # Outras estatísticas podem ser adicionadas aqui (ex: min, max, média para numéricos)
            })
        return details

    def identify_primary_key_candidates(self):
        """
        Identifica colunas que são fortes candidatas a Chave Primária (PK).
        Uma coluna é candidata se atender aos limiares de unicidade e não nulidade.
        """
        pk_candidates_info = []
        column_profiles = self.column_details() # Reutiliza o perfil detalhado

        for col_profile in column_profiles:
            is_strong_candidate = (col_profile["Porcentagem de Unicidade"] >= self.pk_uniqueness_threshold and
                                   col_profile["Porcentagem de Não Nulos"] >= self.pk_non_null_threshold)
            
            if is_strong_candidate: # Ou podemos retornar todas com um flag
                pk_candidates_info.append({
                    "Nome da Coluna": col_profile["Nome da Coluna"],
                    "Porcentagem de Unicidade": col_profile["Porcentagem de Unicidade"],
                    "Porcentagem de Não Nulos": col_profile["Porcentagem de Não Nulos"],
                    "É Candidata Forte a PK": is_strong_candidate 
                    # Poderíamos adicionar mais informações se necessário
                })
        return pk_candidates_info