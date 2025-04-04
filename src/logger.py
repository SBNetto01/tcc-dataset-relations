import logging

# Configuração do logger
logging.basicConfig(
    filename="../logs/app.log", 
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

def log_info(message):
    logging.info(message)
    print(f"INFO: {message}")

def log_error(message):
    logging.error(message)
    print(f"ERROR: {message}")
