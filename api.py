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
    # Alterado para receber Optional[str] para melhor tratamento de vazio/None
    fk_similarity_override: Optional[str] = Form(None, description="Opcional: Sobrescreve o limiar de similaridade (%). Deixe em branco/nulo para usar lógica padrão.")
):
    """
    Analisa todos os arquivos .csv dentro de uma pasta especificada **no servidor**.

    - **folder_path**: Caminho para a pasta contendo os arquivos CSV.
    - **header_option**: Define como os arquivos CSV devem ser lidos.
    - **fk_similarity_override**: Permite forçar um limiar de similaridade específico (ex: 0 ou 30).
    """
    logger.info(f"Recebida requisição para analisar pasta: '{folder_path}' com opção de cabeçalho: {header_option}.")

    # ... (validação da pasta e carregamento dos arquivos - sem alterações aqui) ...
    if not os.path.isdir(folder_path):
        logger.error(f"Caminho fornecido não é um diretório válido: {folder_path}")
        raise HTTPException(status_code=400, detail=f"O caminho fornecido não existe ou não é um diretório: {folder_path}")

    try:
        csv_files = glob.glob(os.path.join(folder_path, "*.csv"))
        if len(csv_files) < 2:
             logger.warning(f"Menos de 2 arquivos CSV encontrados em: {folder_path}")
             raise HTTPException(status_code=400, detail=f"São necessários pelo menos 2 arquivos CSV na pasta '{folder_path}' para análise.")

        loaded_datasets: List[Dict[str, Any]] = []
        logger.info(f"Encontrados {len(csv_files)} arquivos CSV. Carregando...")
        for filepath in csv_files:
            dataset_name = os.path.splitext(os.path.basename(filepath))[0]
            logger.info(f"Carregando arquivo: {filepath}")
            try:
                df = FileHandler.load_csv(filepath, header_option=header_option)
                loaded_datasets.append({'name': dataset_name, 'df': df, 'profile': None})
            except Exception as e:
                logger.error(f"Falha ao carregar o dataset {dataset_name} de {filepath}: {e}")
                continue

        if len(loaded_datasets) < 2:
             raise HTTPException(status_code=400, detail=f"Menos de 2 arquivos CSV puderam ser carregados com sucesso da pasta '{folder_path}'.")

    except Exception as e:
        logger.error(f"Erro ao acessar ou listar arquivos em {folder_path}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao processar a pasta {folder_path}: {str(e)}")


    # --- Determina o limiar de similaridade a ser usado (LÓGICA CORRIGIDA) ---
    current_fk_similarity_threshold: float
    user_provided_override = False

    # Verifica se o usuário forneceu um valor não nulo E não vazio
    if fk_similarity_override is not None and fk_similarity_override.strip() != "":
        try:
            # Tenta converter para float
            current_fk_similarity_threshold = float(fk_similarity_override)
            user_provided_override = True
            logger.info(f"Usando limiar de similaridade de nome fornecido pelo usuário: {current_fk_similarity_threshold}%")
        except ValueError:
            # Se a conversão falhar (ex: usuário digitou texto), loga aviso e usa lógica padrão
            logger.warning(f"Valor inválido '{fk_similarity_override}' fornecido para fk_similarity_override. Ignorando e usando lógica padrão.")
            user_provided_override = False # Garante que caia na lógica padrão abaixo

    # Se nenhum override válido foi fornecido pelo usuário
    if not user_provided_override:
        if header_option in ['generic', 'none']:
            current_fk_similarity_threshold = 0.0 # Força 0 para testes 2 e 3
            logger.info(f"Opção de cabeçalho '{header_option}'. Forçando limiar de similaridade para 0%.")
        else: # header_option == 'infer' (Teste 1)
            current_fk_similarity_threshold = DEFAULT_FK_NAME_SIMILARITY_THRESHOLD
            logger.info(f"Usando limiar de similaridade de nome padrão: {current_fk_similarity_threshold}%")
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    # --- Chama a lógica principal do projeto ---
    try:
        results = analyze_datasets(
            loaded_datasets=loaded_datasets,
            pk_uniqueness_threshold=DEFAULT_PK_UNIQUENESS_THRESHOLD,
            pk_non_null_threshold=DEFAULT_PK_NON_NULL_THRESHOLD,
            fk_inclusion_threshold=DEFAULT_FK_INCLUSION_THRESHOLD,
            fk_name_similarity_threshold=current_fk_similarity_threshold # Passa o valor correto
        )

        if not results:
            logger.info("Análise concluída. Nenhuma relação encontrada.")
            return {"message": "Análise concluída. Nenhuma relação encontrada com os critérios definidos."}

        logger.info(f"Análise concluída com sucesso. Encontradas {len(results)} relações.")
        return {"relations_found": results}
    except Exception as e:
        logger.error(f"Ocorreu um erro durante a fase de análise: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ocorreu um erro durante a análise: {str(e)}")