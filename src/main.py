import os
import glob
import pandas as pd
from typing import List, Dict, Any
import logging
import argparse # Importa o módulo para argumentos de linha de comando

# --- Imports relativos corrigidos para a estrutura do projeto ---
from .components.data_profiler import DataProfiler
from .components.attribute_matcher import AttributeMatcher
from .components.fk_finder import FKFinder
from .utils.logger import setup_logger, LOGGER_NAME
from .utils.file_handler import FileHandler

# --- Configurações Globais / Limiares (Valores Padrão) ---
# Estes agora servem como valores padrão se nenhum argumento for passado
DEFAULT_PK_UNIQUENESS_THRESHOLD = 98.0
DEFAULT_PK_NON_NULL_THRESHOLD = 98.0
DEFAULT_FK_INCLUSION_THRESHOLD = 85.0
DEFAULT_FK_NAME_SIMILARITY_THRESHOLD = 30.0

# --- Lógica Principal Modificada para Aceitar Parâmetros ---
def analyze_datasets(
    loaded_datasets: List[Dict[str, Any]],
    pk_uniqueness_threshold: float,
    pk_non_null_threshold: float,
    fk_inclusion_threshold: float,
    fk_name_similarity_threshold: float # Recebe como parâmetro
) -> List[Dict[str, Any]]:
    """
    Recebe datasets e limiares, retorna as relações de FK encontradas.
    """
    logger = logging.getLogger(LOGGER_NAME)

    # 1. Inicializar componentes usando os limiares recebidos
    attribute_matcher = AttributeMatcher()
    fk_finder = FKFinder(
        attribute_matcher=attribute_matcher,
        inclusion_threshold=fk_inclusion_threshold,
        name_similarity_threshold=fk_name_similarity_threshold # Usa o parâmetro
    )

    logger.info(f"Iniciando perfilamento com limiares PK: Unicidade={pk_uniqueness_threshold}%, Não Nulo={pk_non_null_threshold}%")
    # 2. Perfilar datasets usando os limiares recebidos
    for dataset_info in loaded_datasets:
        logger.info(f"Perfilando dataset: {dataset_info['name']}")
        profiler = DataProfiler(
            dataset_info['df'],
            pk_uniqueness_threshold=pk_uniqueness_threshold, # Usa o parâmetro
            pk_non_null_threshold=pk_non_null_threshold   # Usa o parâmetro
        )
        dataset_info['profile'] = profiler.generate_profile()

    # 3. Identificar Relações FK
    logger.info(f"Iniciando identificação de FKs com limiares: Inclusão={fk_inclusion_threshold}%, Similaridade Nome={fk_name_similarity_threshold}%")
    all_fk_relations: List[Dict[str, Any]] = []
    for i in range(len(loaded_datasets)):
        for j in range(len(loaded_datasets)):
            if i == j: continue
            dataset_A_info = loaded_datasets[i]
            dataset_B_info = loaded_datasets[j]
            if not dataset_A_info.get('profile') or not dataset_B_info.get('profile'): continue

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
    return all_fk_relations

# --- Função de Execução via Script Modificada ---
def main():
    """
    Função para executar a análise a partir de arquivos, aceitando argumentos
    de linha de comando para configuração.
    """
    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # Configuração do Parser de Argumentos
    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    parser = argparse.ArgumentParser(description="Identifica relações de FK entre arquivos CSV.")
    parser.add_argument(
        '--header',
        type=str,
        default='infer',
        choices=['infer', 'generic', 'none'],
        help="Tipo de cabeçalho nos arquivos CSV ('infer', 'generic', 'none'). Padrão: 'infer'."
    )
    parser.add_argument(
        '--pk-unique',
        type=float,
        default=DEFAULT_PK_UNIQUENESS_THRESHOLD,
        help=f"Limiar de unicidade para PK (%). Padrão: {DEFAULT_PK_UNIQUENESS_THRESHOLD}"
    )
    parser.add_argument(
        '--pk-nonnull',
        type=float,
        default=DEFAULT_PK_NON_NULL_THRESHOLD,
        help=f"Limiar de não nulidade para PK (%). Padrão: {DEFAULT_PK_NON_NULL_THRESHOLD}"
    )
    parser.add_argument(
        '--fk-include',
        type=float,
        default=DEFAULT_FK_INCLUSION_THRESHOLD,
        help=f"Limiar de inclusão para FK (%). Padrão: {DEFAULT_FK_INCLUSION_THRESHOLD}"
    )
    parser.add_argument(
        '--fk-sim',
        type=float,
        default=DEFAULT_FK_NAME_SIMILARITY_THRESHOLD,
        help=f"Limiar de similaridade de nome para FK (%). Padrão: {DEFAULT_FK_NAME_SIMILARITY_THRESHOLD}"
    )
    parser.add_argument(
        '--dataset-dir',
        type=str,
        default='datasets',
        help="Diretório onde os arquivos CSV estão localizados. Padrão: 'datasets'"
    )

    args = parser.parse_args()
    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    logger = setup_logger()
    OUTPUT_DIR = 'output'
    RESULTS_FILENAME = "fk_identification_results.txt"
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    logger.info("Iniciando processo de identificação de chaves (modo script).")
    logger.info(f"Usando diretório de datasets: {args.dataset_dir}")
    logger.info(f"Opção de cabeçalho: {args.header}")

    dataset_files = glob.glob(os.path.join(args.dataset_dir, "*.csv"))
    if not dataset_files:
        logger.warning(f"Nenhum arquivo CSV encontrado no diretório: {args.dataset_dir}")
        return

    loaded_datasets: List[Dict[str, Any]] = []

    for filepath in dataset_files:
        dataset_name = os.path.splitext(os.path.basename(filepath))[0]
        try:
            # Usa o argumento --header para carregar o CSV
            df = FileHandler.load_csv(filepath, header_option=args.header)
            loaded_datasets.append({'name': dataset_name, 'df': df, 'profile': None})
        except Exception as e:
            logger.error(f"Falha ao carregar o dataset {dataset_name}: {e}")

    if not loaded_datasets:
        logger.error("Nenhum dataset foi carregado. Encerrando.")
        return

    # Chama a lógica de análise principal passando os argumentos da linha de comando
    all_fk_relations = analyze_datasets(
        loaded_datasets=loaded_datasets,
        pk_uniqueness_threshold=args.pk_unique,
        pk_non_null_threshold=args.pk_nonnull,
        fk_inclusion_threshold=args.fk_include,
        fk_name_similarity_threshold=args.fk_sim
    )

    logger.info("--- Sumário dos Resultados ---")
    if not all_fk_relations:
        logger.info("Nenhuma relação de FK foi identificada.")
        print("Nenhuma relação de FK foi identificada.")
    else:
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