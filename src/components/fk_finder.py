# src/components/fk_finder.py

import pandas as pd
from typing import List, Dict, Any
# Supondo que data_profiler.py e attribute_matcher.py estão no mesmo diretório (components)
from .attribute_matcher import AttributeMatcher 
# Não precisamos importar DataProfiler aqui, pois esperamos receber os perfis já gerados.

class FKFinder:
    def __init__(self, 
                 attribute_matcher: AttributeMatcher,
                 inclusion_threshold: float = 90.0,
                 name_similarity_threshold: float = 0.0): # 0.0 para não filtrar por nome por padrão
        """
        Inicializa o FKFinder.

        Args:
            attribute_matcher (AttributeMatcher): Instância do comparador de atributos para nomes.
            inclusion_threshold (float): Limiar mínimo (0-100) de inclusão de valores da FK na PK
                                         para considerar uma relação válida.
            name_similarity_threshold (float): Limiar mínimo (0-100) de similaridade de nomes
                                               para considerar um par. Pode ser usado para pré-filtragem
                                               ou apenas como informação. Se 0, não filtra.
        """
        if not isinstance(attribute_matcher, AttributeMatcher):
            raise ValueError("attribute_matcher deve ser uma instância da classe AttributeMatcher.")
        
        self.attribute_matcher = attribute_matcher
        self.inclusion_threshold = inclusion_threshold
        self.name_similarity_threshold = name_similarity_threshold

    def _check_type_compatibility(self, dtype_fk: str, dtype_pk: str) -> bool:
        """
        Verifica se os tipos de dados da FK potencial e da PK são compatíveis.
        Esta é uma verificação que pode ser expandida conforme necessário.
        Os tipos são strings obtidas do DataProfiler.
        """
        dtype_fk_lower = dtype_fk.lower()
        dtype_pk_lower = dtype_pk.lower()

        # Regra básica: tipos devem ser da mesma categoria geral
        # Exemplo: 'int64' e 'int32' são compatíveis. 'int64' e 'float64' podem ser (com ressalvas).
        # 'object' (string) com 'object'.
        
        if 'int' in dtype_fk_lower and 'int' in dtype_pk_lower:
            return True
        if 'float' in dtype_fk_lower and 'float' in dtype_pk_lower:
            return True
        # Considerar int como FK para float como PK (e vice-versa) pode ser arriscado
        # dependendo da precisão, mas poderia ser uma regra opcional.
        # if ('int' in dtype_fk_lower and 'float' in dtype_pk_lower) or \
        #    ('float' in dtype_fk_lower and 'int' in dtype_pk_lower):
        # return True # Cuidado com perda de precisão ou falhas de matching

        if 'object' in dtype_fk_lower and 'object' in dtype_pk_lower: # 'object' geralmente são strings
            return True
        if 'datetime' in dtype_fk_lower and 'datetime' in dtype_pk_lower:
            return True
        if 'bool' in dtype_fk_lower and 'bool' in dtype_pk_lower:
            return True
            
        # Se os tipos são exatamente os mesmos (ex: 'category' com 'category')
        if dtype_fk_lower == dtype_pk_lower:
            return True
            
        return False

    def _calculate_inclusion_percentage(self, fk_series: pd.Series, pk_series: pd.Series) -> float:
        """
        Calcula a porcentagem de valores únicos não nulos da série FK que estão presentes 
        nos valores únicos não nulos da série PK.
        """
        # Tratar series que podem ser completamente nulas ou de tipos inesperados
        if fk_series.empty or pk_series.empty:
            return 0.0

        try:
            fk_non_null_values = fk_series.dropna().unique()
            # Otimização: converter pk_unique_values para set para buscas O(1) em média
            pk_unique_values = set(pk_series.dropna().unique()) 
        except Exception: # Captura erros se .unique() falhar em tipos não usuais
            return 0.0


        if len(fk_non_null_values) == 0:
            # Se a coluna FK (após dropna) não tem valores, não há o que verificar.
            # Considerar 0% de inclusão, pois não há evidência positiva.
            # Alguns poderiam argumentar 100% se não há violações, mas 0% é mais conservador.
            return 0.0

        contained_count = 0
        for val in fk_non_null_values:
            if val in pk_unique_values:
                contained_count += 1
        
        return (contained_count / len(fk_non_null_values)) * 100

    def identify_fk_relations(self, 
                              df_fk_potential: pd.DataFrame, 
                              df_pk_provider: pd.DataFrame,
                              profile_fk_potential: Dict[str, Any], 
                              profile_pk_provider: Dict[str, Any],
                              fk_df_name: str = "ForeignKeyTable", 
                              pk_df_name: str = "PrimaryKeyTable") -> List[Dict[str, Any]]:
        """
        Identifica potenciais relações de FK entre dois DataFrames.

        Args:
            df_fk_potential (pd.DataFrame): DataFrame que pode conter as FKs.
            df_pk_provider (pd.DataFrame): DataFrame que provê as PKs.
            profile_fk_potential (Dict[str, Any]): Perfil do df_fk_potential (gerado pelo DataProfiler).
            profile_pk_provider (Dict[str, Any]): Perfil do df_pk_provider (gerado pelo DataProfiler).
            fk_df_name (str): Nome do DataFrame de FKs para o relatório.
            pk_df_name (str): Nome do DataFrame de PKs para o relatório.

        Returns:
            List[Dict[str, Any]]: Uma lista de dicionários, cada um representando uma relação FK-PK candidata.
        """
        found_relations: List[Dict[str, Any]] = []
        
        pk_candidates_profile = profile_pk_provider.get("Candidatas a Chave Primária", [])
        if not pk_candidates_profile:
            # logger.info(f"Nenhuma candidata a PK encontrada em {pk_df_name}.") # Adicionar logging depois
            return [] 

        # Criar dicionários para acesso rápido aos detalhes das colunas (como tipo de dado)
        fk_col_details_map = {col['Nome da Coluna']: col for col in profile_fk_potential.get("Perfil Detalhado das Colunas", [])}
        pk_col_details_map = {col['Nome da Coluna']: col for col in profile_pk_provider.get("Perfil Detalhado das Colunas", [])}

        for fk_col_name in df_fk_potential.columns:
            fk_col_profile = fk_col_details_map.get(fk_col_name)
            if not fk_col_profile:
                # logger.warning(f"Perfil não encontrado para coluna FK {fk_col_name} em {fk_df_name}.")
                continue # Pula se não há perfil para a coluna FK
            
            dtype_fk = fk_col_profile["Tipo de Dado"]

            for pk_candidate_info in pk_candidates_profile:
                pk_col_name = pk_candidate_info["Nome da Coluna"]
                pk_col_profile = pk_col_details_map.get(pk_col_name)
                
                if not pk_col_profile:
                    # logger.warning(f"Perfil não encontrado para coluna PK {pk_col_name} em {pk_df_name}.")
                    continue # Pula se não há perfil para a coluna PK

                dtype_pk = pk_col_profile["Tipo de Dado"]

                # 1. Verificar compatibilidade de tipo
                if not self._check_type_compatibility(dtype_fk, dtype_pk):
                    continue

                # 2. Heurística de Similaridade de Nomes (opcional, pode ser usada para filtrar ou apenas informar)
                name_similarity_score = self.attribute_matcher.get_name_similarity(fk_col_name, pk_col_name)
                if name_similarity_score < self.name_similarity_threshold:
                    # Se o limiar de similaridade de nome for > 0 e o score for menor, pula.
                    # Se o limiar for 0, este 'if' nunca será verdadeiro, então não filtra por nome.
                    continue 

                # 3. Verificar Dependência de Inclusão (a parte mais custosa)
                fk_series = df_fk_potential[fk_col_name]
                pk_series = df_pk_provider[pk_col_name]
                
                inclusion_perc = self._calculate_inclusion_percentage(fk_series, pk_series)

                if inclusion_perc >= self.inclusion_threshold:
                    relation_info = {
                        "FK_DataFrame_Name": fk_df_name,
                        "FK_Column": fk_col_name,
                        "FK_DataType": dtype_fk,
                        "PK_DataFrame_Name": pk_df_name,
                        "PK_Column": pk_col_name,
                        "PK_DataType": dtype_pk,
                        "Inclusion_Percentage": round(inclusion_perc, 2),
                        "Name_Similarity_Score": round(name_similarity_score, 2)
                    }
                    found_relations.append(relation_info)
        
        # Ordenar as relações encontradas, por exemplo, pela porcentagem de inclusão e similaridade de nome
        found_relations.sort(key=lambda x: (x["Inclusion_Percentage"], x["Name_Similarity_Score"]), reverse=True)
        
        return found_relations