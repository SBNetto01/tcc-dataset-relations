import os
import glob # Para encontrar arquivos de dataset
import pandas as pd
from typing import List, Dict, Any # Para type hinting

# Componentes do projeto
from components.data_profiler import DataProfiler
from components.attribute_matcher import AttributeMatcher
from components.fk_finder import FKFinder

# Utilitários
from utils.logger import setup_logger #
from utils.file_handler import FileHandler #
# Para exportação, vamos definir uma nova função ou adaptar depois
# from utils.result_exporter import export_fk_results # Supondo que criaremos esta

# --- Configurações Globais ---
DATASET_DIR = 'datasets'
OUTPUT_DIR = 'output'
PK_UNIQUENESS_THRESHOLD = 98.0  # % de unicidade para ser PK
PK_NON_NULL_THRESHOLD = 98.0    # % de não nulos para ser PK
FK_INCLUSION_THRESHOLD = 85.0   # % de valores da FK contidos na PK
FK_NAME_SIMILARITY_THRESHOLD = 30.0 # % Similaridade de nome (0 para não filtrar, apenas informar)
RESULTS_FILENAME = "fk_identification_results.txt"

# Garante que o diretório de output exista
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Configura o logger
logger = setup_logger(log_folder="logs") 


def format_fk_results_for_export(fk_relations: List[Dict[str, Any]]) -> str:
    """
    Formata a lista de relações FK encontradas para uma string legível.
    """
    if not fk_relations:
        return "Nenhuma relação de Chave Estrangeira (FK) encontrada com os critérios definidos."

    lines = ["--- Resultados da Identificação de Chaves Estrangeiras (FKs) ---"]
    for rel in fk_relations:
        line = (
            f"FK: {rel['FK_DataFrame_Name']}.[{rel['FK_Column']}] ({rel['FK_DataType']}) "
            f"--> PK: {rel['PK_DataFrame_Name']}.[{rel['PK_Column']}] ({rel['PK_DataType']})\n"
            f"  Inclusão: {rel['Inclusion_Percentage']}% | Similaridade de Nome: {rel['Name_Similarity_Score']}%\n"
            f"  ------------------------------------------------------------"
        )
        lines.append(line)
    return "\n".join(lines)


def main():
    logger.info("Iniciando processo de identificação de chaves PK e FK.")
    
    # 1. Inicializar componentes
    attribute_matcher = AttributeMatcher()
    fk_finder = FKFinder(
        attribute_matcher=attribute_matcher,
        inclusion_threshold=FK_INCLUSION_THRESHOLD,
        name_similarity_threshold=FK_NAME_SIMILARITY_THRESHOLD
    )

    # 2. Carregar datasets
    dataset_files = glob.glob(os.path.join(DATASET_DIR, "*.csv")) # Apenas CSV por enquanto
    if not dataset_files:
        logger.warning(f"Nenhum arquivo CSV encontrado no diretório: {DATASET_DIR}")
        return

    loaded_datasets: List[Dict[str, Any]] = []
    for filepath in dataset_files:
        dataset_name = os.path.splitext(os.path.basename(filepath))[0]
        logger.info(f"Carregando dataset: {dataset_name} de {filepath}")
        try:
            # Usando FileHandler para carregar
            df = FileHandler.load_csv(filepath) 
            loaded_datasets.append({'name': dataset_name, 'df': df, 'profile': None, 'filepath': filepath})
            logger.info(f"Dataset {dataset_name} carregado com {len(df)} linhas e {len(df.columns)} colunas.")
        except IOError as e:
            logger.error(f"Falha ao carregar o dataset {dataset_name} de {filepath}: {e}")
        except Exception as e: # Captura outras exceções inesperadas do pandas, por exemplo
            logger.error(f"Erro inesperado ao processar o arquivo {filepath}: {e}")


    if not loaded_datasets:
        logger.error("Nenhum dataset foi carregado com sucesso. Encerrando.")
        return

    # 3. Perfilar datasets e identificar PKs
    logger.info("--- Fase de Perfilamento e Identificação de PKs ---")
    for dataset_info in loaded_datasets:
        logger.info(f"Perfilando dataset: {dataset_info['name']}")
        profiler = DataProfiler(
            dataset_info['df'],
            pk_uniqueness_threshold=PK_UNIQUENESS_THRESHOLD,
            pk_non_null_threshold=PK_NON_NULL_THRESHOLD
        )
        dataset_info['profile'] = profiler.generate_profile()
        
        pk_candidates = dataset_info['profile'].get("Candidatas a Chave Primária", [])
        if pk_candidates:
            logger.info(f"Candidatas a PK para {dataset_info['name']}:")
            for pkc in pk_candidates:
                logger.info(f"  - Coluna: {pkc['Nome da Coluna']}, Unicidade: {pkc['Porcentagem de Unicidade']}%, Não Nulos: {pkc['Porcentagem de Não Nulos']}%")
        else:
            logger.info(f"Nenhuma candidata forte a PK encontrada para {dataset_info['name']} com os limiares definidos.")

    # 4. Identificar Relações FK (entre pares de datasets)
    logger.info("--- Fase de Identificação de FKs ---")
    all_fk_relations: List[Dict[str, Any]] = []

    for i in range(len(loaded_datasets)):
        for j in range(len(loaded_datasets)): # Compara todos com todos, incluindo consigo mesmo (raro para FKs, mas o FKFinder deve lidar)
            if i == j: # Não comparar um dataset consigo mesmo para FKs (a menos que seja um requisito específico)
                # Ou podemos permitir e ver se o FKFinder encontra algo (ex: self-referencing keys)
                # Por enquanto, para FKs entre tabelas distintas, vamos pular.
                # Se quiser self-referencing, remova este if.
                continue

            dataset_A_info = loaded_datasets[i]
            dataset_B_info = loaded_datasets[j]

            # Evita processar se algum perfil não foi gerado (ex: DF vazio ou erro no profiler)
            if not dataset_A_info['profile'] or not dataset_B_info['profile']:
                logger.warning(f"Skipping FK check between {dataset_A_info['name']} and {dataset_B_info['name']} due to missing profile(s).")
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
                logger.info(f"Encontradas {len(fk_relations_A_to_B)} potenciais FKs de {dataset_A_info['name']} para {dataset_B_info['name']}.")
                all_fk_relations.extend(fk_relations_A_to_B)
            # else: # Opcional: logar quando nada é encontrado
                # logger.info(f"Nenhuma FK encontrada de {dataset_A_info['name']} para {dataset_B_info['name']}.")


    # 5. Apresentar e Exportar Resultados
    logger.info("--- Sumário dos Resultados ---")
    if not all_fk_relations:
        logger.info("Nenhuma relação de Chave Estrangeira (FK) foi identificada entre os datasets processados.")
        print("Nenhuma relação de Chave Estrangeira (FK) foi identificada.")
    else:
        logger.info(f"Total de {len(all_fk_relations)} potenciais relações FK identificadas.")
        # Imprimir no console
        print("\n\n--- Relações de Chave Estrangeira (FKs) Encontradas ---")
        formatted_results_string = format_fk_results_for_export(all_fk_relations)
        print(formatted_results_string)
        
        # Exportar para arquivo
        output_filepath = os.path.join(OUTPUT_DIR, RESULTS_FILENAME)
        try:
            FileHandler.save_text(output_filepath, formatted_results_string) #
            logger.info(f"Resultados da identificação de FKs exportados para: {output_filepath}")
            print(f"\nResultados também salvos em: {output_filepath}")
        except IOError as e:
            logger.error(f"Erro ao salvar resultados em {output_filepath}: {e}")
            print(f"Erro ao salvar resultados em {output_filepath}: {e}")
            
    logger.info("Processo de identificação de chaves finalizado.")

if __name__ == '__main__':
    main()