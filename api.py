import pandas as pd
from fastapi import FastAPI, UploadFile, HTTPException
from typing import List

# --- Imports do Projeto ---
# Importa a função de análise principal
from src.main import analyze_datasets
# Importa o setup do logger e a constante com o nome
from src.utils.logger import setup_logger

# --- Configuração Inicial ---
# Configura o logger no ponto de entrada da API.
# Todas as chamadas subsequentes ao logger usarão esta configuração.
logger = setup_logger()

# Cria a aplicação FastAPI
app = FastAPI(
    title="Data Relation Finder API",
    description="Uma API para identificar relações de chave estrangeira entre datasets CSV.",
    version="1.0.0"
)

@app.post("/analyze/", summary="Analisa múltiplos arquivos CSV para encontrar relações")
async def analyze_csv_files(files: List[UploadFile]):
    """
    Faça o upload de 2 ou mais arquivos CSV para analisá-los e descobrir
    potenciais relações de chave estrangeira entre eles.
    """
    logger.info(f"Recebida requisição de análise para {len(files)} arquivos.")
    
    if len(files) < 2:
        logger.warning("Requisição recebida com menos de 2 arquivos. Retornando erro.")
        raise HTTPException(status_code=400, detail="Por favor, envie pelo menos 2 arquivos CSV.")

    loaded_datasets = []
    for file in files:
        # Validação do tipo de arquivo
        if file.content_type != 'text/csv':
            logger.warning(f"Arquivo '{file.filename}' com tipo de conteúdo inválido: {file.content_type}")
            raise HTTPException(status_code=400, detail=f"Arquivo '{file.filename}' não é um CSV válido.")
        
        # Carrega o arquivo enviado em um DataFrame Pandas
        try:
            logger.info(f"Processando arquivo: {file.filename}")
            df = pd.read_csv(file.file)
            # É importante resetar o ponteiro do arquivo para o caso de precisar ler de novo
            file.file.seek(0)
            
            dataset_info = {
                'name': file.filename.replace('.csv', ''),
                'df': df,
                'profile': None
            }
            loaded_datasets.append(dataset_info)
        except Exception as e:
            logger.error(f"Erro ao processar o arquivo {file.filename}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Erro ao processar o arquivo {file.filename}: {str(e)}")

    # Chama a lógica principal do projeto com os datasets carregados
    try:
        results = analyze_datasets(loaded_datasets)
        
        if not results:
            logger.info("Análise concluída. Nenhuma relação encontrada.")
            return {"message": "Análise concluída. Nenhuma relação encontrada com os critérios definidos."}
        
        logger.info(f"Análise concluída com sucesso. Encontradas {len(results)} relações.")
        return {"relations_found": results}
    except Exception as e:
        logger.error(f"Ocorreu um erro durante a fase de análise: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ocorreu um erro durante a análise: {str(e)}")