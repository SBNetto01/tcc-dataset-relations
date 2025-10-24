import pandas as pd
from fastapi import FastAPI, HTTPException, Form
from typing import List, Dict, Any, Optional # Adicionado Optional
import os
import glob

# --- Imports do Projeto ---
from src.main import analyze_datasets
from src.main import (
    DEFAULT_PK_UNIQUENESS_THRESHOLD,
    DEFAULT_PK_NON_NULL_THRESHOLD,
    DEFAULT_FK_INCLUSION_THRESHOLD,
    DEFAULT_FK_NAME_SIMILARITY_THRESHOLD
)
from src.utils.logger import setup_logger
from src.utils.file_handler import FileHandler

# --- Configuração Inicial ---
logger = setup_logger()

app = FastAPI(
    title="Data Relation Finder API",
    description="Uma API para identificar relações de chave estrangeira entre datasets CSV em uma pasta do servidor.",
    version="1.2.2" # Versão atualizada
)

@app.post("/analyze_folder/", summary="Analisa arquivos CSV de uma pasta no servidor")
async def analyze_csv_folder(
    folder_path: str = Form(...),
    header_option: str = Form("infer", enum=["infer", "generic", "none"]),
    separator: Optional[str] = Form(None, description="Opcional: Força um separador (ex: ',' ou ';'). Deixe em branco/nulo para detecção automática."),
    
    # --- Parâmetros de Limiar ---
    pk_unique_override: Optional[str] = Form(None, description="Opcional: Sobrescreve o limiar de UNICIDADE da PK (%). Deixe em branco/nulo para usar o padrão."),
    pk_nonnull_override: Optional[str] = Form(None, description="Opcional: Sobrescreve o limiar de NÃO NULOS da PK (%). Deixe em branco/nulo para usar o padrão."),
    fk_similarity_override: Optional[str] = Form(None, description="Opcional: Sobrescreve o limiar de SIMILARIDADE DE NOME (%). Deixe em branco/nulo para usar lógica padrão."),
    
    # +++ NOVO PARÂMETRO ADICIONADO +++
    fk_inclusion_override: Optional[str] = Form(None, description="Opcional: Sobrescreve o limiar de INCLUSÃO da FK (%). Deixe em branco/nulo para usar o padrão.")
    # +++++++++++++++++++++++++++++++++
):
    """
    Analisa todos os arquivos .csv dentro de uma pasta especificada **no servidor**.

    - **folder_path**: Caminho para a pasta contendo os arquivos CSV.
    - **header_option**: Define como os arquivos CSV devem ser lidos.
    - **separator**: (Opcional) O separador de colunas (ex: ',' ou ';').
    - **pk_unique_override**: (Opcional) Limiar de unicidade da PK (ex: 90).
    - **pk_nonnull_override**: (Opcional) Limiar de não nulidade da PK (ex: 90).
    - **fk_similarity_override**: (Opcional) Limiar de similaridade de nome (ex: 0 ou 30).
    - **fk_inclusion_override**: (Opcional) Limiar de inclusão da FK (ex: 85).
    """
    logger.info(f"Recebida requisição para analisar pasta: '{folder_path}' com opção de cabeçalho: {header_option}.")

    # ... (validação da pasta) ...
    if not os.path.isdir(folder_path):
        logger.error(f"Caminho fornecido não é um diretório válido: {folder_path}")
        raise HTTPException(status_code = 400, detail=f"O caminho fornecido não existe ou não é um diretório: {folder_path}")

    try:
        csv_files = glob.glob(os.path.join(folder_path, "*.csv"))
        if len(csv_files) < 2:
             logger.warning(f"Menos de 2 arquivos CSV encontrados em: {folder_path}")
             raise HTTPException(status_code = 400, detail=f"São necessários pelo menos 2 arquivos CSV na pasta '{folder_path}' para análise.")

        loaded_datasets: List[Dict[str, Any]] = []
        logger.info(f"Encontrados {len(csv_files)} arquivos CSV. Carregando...")
        for filepath in csv_files:
            dataset_name = os.path.splitext(os.path.basename(filepath))[0]
            logger.info(f"Carregando arquivo: {filepath}")
            try:
                # Passando o separador para o File Handler
                df = FileHandler.load_csv(filepath, header_option=header_option, separator=separator)
                
                logger.info(f"Arquivo {dataset_name} carregado com sucesso. Shape: {df.shape}")
                loaded_datasets.append({'name': dataset_name, 'df': df, 'profile': None})
            except Exception as e:
                logger.error(f"Falha ao carregar o dataset {dataset_name} de {filepath}: {e}")
                continue

        if len(loaded_datasets) < 2:
             raise HTTPException(status_code = 400, detail=f"Menos de 2 arquivos CSV puderam ser carregados com sucesso da pasta '{folder_path}'.")

    except Exception as e:
        logger.error(f"Erro ao acessar ou listar arquivos em {folder_path}: {str(e)}")
        raise HTTPException(status_code = 500, detail=f"Erro ao processar a pasta {folder_path}: {str(e)}")


    # --- Determina o limiar de UNICIDADE PK ---
    current_pk_unique_threshold: float
    if pk_unique_override is not None and pk_unique_override.strip() != "":
        try:
            current_pk_unique_threshold = float(pk_unique_override)
            logger.info(f"Usando limiar de UNICIDADE PK fornecido pelo usuário: {current_pk_unique_threshold}%")
        except ValueError:
            logger.warning(f"Valor inválido '{pk_unique_override}' para pk_unique_override. Usando padrão {DEFAULT_PK_UNIQUENESS_THRESHOLD}%.")
            current_pk_unique_threshold = DEFAULT_PK_UNIQUENESS_THRESHOLD
    else:
        current_pk_unique_threshold = DEFAULT_PK_UNIQUENESS_THRESHOLD
        logger.info(f"Usando limiar de UNICIDADE PK padrão: {current_pk_unique_threshold}%")

    # --- Determina o limiar de NÃO NULOS PK ---
    current_pk_nonnull_threshold: float
    if pk_nonnull_override is not None and pk_nonnull_override.strip() != "":
        try:
            current_pk_nonnull_threshold = float(pk_nonnull_override)
            logger.info(f"Usando limiar de NÃO NULOS PK fornecido pelo usuário: {current_pk_nonnull_threshold}%")
        except ValueError:
            logger.warning(f"Valor inválido '{pk_nonnull_override}' para pk_nonnull_override. Usando padrão {DEFAULT_PK_NON_NULL_THRESHOLD}%.")
            current_pk_nonnull_threshold = DEFAULT_PK_NON_NULL_THRESHOLD
    else:
        current_pk_nonnull_threshold = DEFAULT_PK_NON_NULL_THRESHOLD
        logger.info(f"Usando limiar de NÃO NULOS PK padrão: {current_pk_nonnull_threshold}%")
        
    
    # +++ LÓGICA ADICIONADA PARA LIMIAR DE INCLUSÃO FK +++
    current_fk_inclusion_threshold: float
    if fk_inclusion_override is not None and fk_inclusion_override.strip() != "":
        try:
            current_fk_inclusion_threshold = float(fk_inclusion_override)
            logger.info(f"Usando limiar de INCLUSÃO FK fornecido pelo usuário: {current_fk_inclusion_threshold}%")
        except ValueError:
            logger.warning(f"Valor inválido '{fk_inclusion_override}' para fk_inclusion_override. Usando padrão {DEFAULT_FK_INCLUSION_THRESHOLD}%.")
            current_fk_inclusion_threshold = DEFAULT_FK_INCLUSION_THRESHOLD
    else:
        current_fk_inclusion_threshold = DEFAULT_FK_INCLUSION_THRESHOLD
        logger.info(f"Usando limiar de INCLUSÃO FK padrão: {current_fk_inclusion_threshold}%")
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++


    # --- Lógica de similaridade de FK (Lógica de prioridade corrigida) ---
    current_fk_similarity_threshold: float

    # A lógica de cabeçalho 'generic' ou 'none' tem prioridade MÁXIMA.
    if header_option in ['generic', 'none']:
        current_fk_similarity_threshold = 0.0
        logger.info(f"Opção de cabeçalho '{header_option}'. Forçando limiar de similaridade para 0%, ignorando qualquer override.")
    
    # Se o cabeçalho for 'infer', então verificamos se há um override.
    else: # header_option == 'infer'
        user_provided_override = False
        if fk_similarity_override is not None and fk_similarity_override.strip() != "":
            try:
                # Tenta converter para float
                current_fk_similarity_threshold = float(fk_similarity_override)
                user_provided_override = True
                logger.info(f"Usando limiar de similaridade de nome fornecido pelo usuário: {current_fk_similarity_threshold}%")
            except ValueError:
                # Se a conversão falhar...
                logger.warning(f"Valor inválido '{fk_similarity_override}' fornecido para fk_similarity_override. Usando padrão.")
                user_provided_override = False
        
        # Se nenhum override válido foi fornecido (ou era inválido)
        if not user_provided_override:
            current_fk_similarity_threshold = DEFAULT_FK_NAME_SIMILARITY_THRESHOLD
            logger.info(f"Usando limiar de similaridade de nome padrão: {current_fk_similarity_threshold}%")

    # --- Chama a lógica principal do projeto ---
    try:
        results = analyze_datasets(
            loaded_datasets=loaded_datasets,
            pk_uniqueness_threshold=current_pk_unique_threshold,
            pk_non_null_threshold=current_pk_nonnull_threshold,
            fk_inclusion_threshold=current_fk_inclusion_threshold, # <<< VALOR ATUALIZADO
            fk_name_similarity_threshold=current_fk_similarity_threshold 
        )

        if not results:
            logger.info("Análise concluída. Nenhuma relação encontrada.")
            return {"message": "Análise concluída. Nenhuma relação encontrada com os critérios definidos."}

        logger.info(f"Análise concluída com sucesso. Encontradas {len(results)} relações.")
        return {"relations_found": results}
    except Exception as e:
        logger.error(f"Ocorreu um erro durante a fase de análise: {str(e)}")
        raise HTTPException(status_code = 500, detail=f"Ocorreu um erro durante a análise: {str(e)}")