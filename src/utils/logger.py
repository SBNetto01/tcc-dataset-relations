import logging
import os
from datetime import datetime

def setup_logger(log_folder='logs', log_level_str='INFO'): # Adicionado log_level_str
    if not os.path.exists(log_folder):
        os.makedirs(log_folder)

    log_file = os.path.join(log_folder, f'log_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt')

    # Converte a string do nível de log para o valor numérico correspondente
    numeric_level = getattr(logging, log_level_str.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {log_level_str}')

    logger = logging.getLogger('tcc_logger')
    logger.setLevel(numeric_level) # Usa o nível de log passado como argumento

    # Verifica se já existem handlers para evitar duplicação
    if not logger.handlers:
        file_handler = logging.FileHandler(log_file)
        # Mudança no formato para incluir o nome do logger e o nome do módulo
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(module)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger