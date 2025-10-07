import os
import glob
import pandas as pd
from typing import List, Dict, Any
import logging

# --- Imports relativos corrigidos para a estrutura do projeto ---
from .components.data_profiler import DataProfiler
from .components.attribute_matcher import AttributeMatcher
from .components.fk_finder import FKFinder
from .utils.logger import setup_logger, LOGGER_NAME
from .utils.file_handler import FileHandler

# --- Configurações Globais / Limiares ---
# Estes valores são usados pela função analyze_datasets
PK_UNIQUENESS_THRESHOLD = 98.0
PK_NON_NULL_THRESHOLD = 98.0
FK_INCLUSION_THRESHOLD = 85.0
FK_NAME_SIMILARITY_THRESHOLD = 30.0

# --- Lógica Principal Abstraída para a API ---
def analyze_datasets(loaded_datasets: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Recebe uma lista de datasets carregados (em memória) e retorna as relações de FK encontradas.
    Esta é a função principal que a API irá chamar.
    """
    # Pega o logger que já foi configurado no ponto de entrada (main() ou api.py)
    logger = logging.getLogger(LOGGER_NAME)

    # 1. Inicializar componentes
    attribute_matcher = AttributeMatcher()
    fk_finder = FKFinder(
        attribute_matcher=attribute_matcher,
        inclusion_threshold=FK_INCLUSION_THRESHOLD,
        name_similarity_threshold=FK_NAME_SIMILARITY_THRESHOLD
    )

    logger.info(f"Iniciando perfilamento para {len(loaded_datasets)} datasets.")
    # 2. Perfilar datasets e identificar PKs
    for dataset_info in loaded_datasets:
        logger.info(f"Perfilando dataset: {dataset_info['name']}")
        profiler = DataProfiler(
            dataset_info['df'],
            pk_uniqueness_threshold=PK_UNIQUENESS_THRESHOLD,
            pk_non_null_threshold=PK_NON_NULL_THRESHOLD
        )
        dataset_info['profile'] = profiler.generate_profile()

    # 3. Identificar Relações FK
    logger.info("Iniciando fase de identificação de FKs.")
    all_fk_relations: List[Dict[str, Any]] = []
    for i in range(len(loaded_datasets)):
        for j in range(len(loaded_datasets)):
            if i == j:
                continue

            dataset_A_info = loaded_datasets[i]
            dataset_B_info = loaded_datasets[j]

            if not dataset_A_info.get('profile') or not dataset_B_info.get('profile'):
                continue
            
            logger.info(f"Verificando FKs de {dataset_A_info['name']} para PKs em {dataset_B_info['name']}")
            
            fk_relations_A_to_B = fk_finder.identify_fk_relations(
                df_fk_potential=dataset_A_info['df'],
                df_pk_provider=dataset_B_info['df'],
                profile_fk_potential=dataset_A_info['profile'],
                profile_pk_provider=dataset_B_info['profile'],
                fk_df_name=dataset_A_info['name'],
                pk_df_name=dataset_B_info['name']
            )
            
            if fk_relations_A_to_B:
                logger.info(f"Encontradas {len(fk_relations_A_to_B)} potenciais FKs.")
                all_fk_relations.extend(fk_relations_A_to_B)

    logger.info(f"Análise concluída. Total de {len(all_fk_relations)} relações encontradas.")
    # 4. Retornar os resultados em formato de lista de dicionários (JSON-friendly)
    return all_fk_relations

# --- Função de Execução via Script (legado) ---
# Esta parte mantém a funcionalidade original de rodar o programa como um script independente.
def main():
    """
    Função para executar a análise a partir de arquivos em um diretório,
    mantendo o comportamento original do script.
    """
    # --- Configura o logger AQUI, no ponto de entrada do script ---
    logger = setup_logger()
    
    # --- Configurações para execução local ---
    DATASET_DIR = 'datasets'
    OUTPUT_DIR = 'output'
    RESULTS_FILENAME = "fk_identification_results.txt"
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    logger.info("Iniciando processo de identificação de chaves (modo script).")

    # Carregar datasets do diretório local
    dataset_files = glob.glob(os.path.join(DATASET_DIR, "*.csv"))
    if not dataset_files:
        logger.warning(f"Nenhum arquivo CSV encontrado no diretório: {DATASET_DIR}")
        return

    loaded_datasets: List[Dict[str, Any]] = []
    for filepath in dataset_files:
        dataset_name = os.path.splitext(os.path.basename(filepath))[0]
        try:
            df = FileHandler.load_csv(filepath)
            loaded_datasets.append({'name': dataset_name, 'df': df, 'profile': None})
        except Exception as e:
            logger.error(f"Falha ao carregar o dataset {dataset_name}: {e}")
    
    if not loaded_datasets:
        logger.error("Nenhum dataset foi carregado. Encerrando.")
        return

    # Chamar a lógica de análise principal
    all_fk_relations = analyze_datasets(loaded_datasets)

    # Apresentar e exportar os resultados
    logger.info("--- Sumário dos Resultados ---")
    if not all_fk_relations:
        logger.info("Nenhuma relação de FK foi identificada.")
        print("Nenhuma relação de FK foi identificada.")
    else:
        # Formatar resultados para exportação
        lines = ["--- Resultados da Identificação de Chaves Estrangeiras (FKs) ---"]
        for rel in all_fk_relations:
            line = (
                f"FK: {rel['FK_DataFrame_Name']}.[{rel['FK_Column']}] ({rel['FK_DataType']}) "
                f"--> PK: {rel['PK_DataFrame_Name']}.[{rel['PK_Column']}] ({rel['PK_DataType']})\n"
                f"  Inclusão: {rel['Inclusion_Percentage']}% | Similaridade de Nome: {rel['Name_Similarity_Score']}%\n"
                f"  ------------------------------------------------------------"
            )
            lines.append(line)
        formatted_results_string = "\n".join(lines)
        
        print(formatted_results_string)
        
        output_filepath = os.path.join(OUTPUT_DIR, RESULTS_FILENAME)
        try:
            FileHandler.save_text(output_filepath, formatted_results_string)
            logger.info(f"Resultados exportados para: {output_filepath}")
        except IOError as e:
            logger.error(f"Erro ao salvar resultados em {output_filepath}: {e}")
            
    logger.info("Processo de identificação de chaves finalizado.")


if __name__ == '__main__':
    main()