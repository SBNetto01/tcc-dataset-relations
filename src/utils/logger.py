# Em src/utils/logger.py
import logging
import os
from datetime import datetime

# Define um nome constante para o logger
LOGGER_NAME = 'DataRelationFinder'

def setup_logger(log_folder='logs', log_level_str='INFO'):
    if not os.path.exists(log_folder):
        os.makedirs(log_folder)

    log_file = os.path.join(log_folder, f'log_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt')
    
    numeric_level = getattr(logging, log_level_str.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {log_level_str}')

    # Sempre pega o logger pelo mesmo nome
    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(numeric_level)
    
    # Limpa handlers existentes para evitar duplicação em re-execuções
    if logger.hasHandlers():
        logger.handlers.clear()

    # Configura o handler do arquivo
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(numeric_level)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(module)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Adiciona um handler para o console também (opcional, mas bom para debug)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger