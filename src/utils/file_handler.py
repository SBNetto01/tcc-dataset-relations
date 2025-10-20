# Em: src/utils/file_handler.py
import pandas as pd
import os
import logging
from .logger import LOGGER_NAME

logger = logging.getLogger(LOGGER_NAME)

class FileHandler:

    @staticmethod
    def _process_csv(source, header_option: str, encoding: str):
        """
        Função auxiliar privada para processar a leitura de CSV com base nas opções.
        'source' pode ser um caminho de arquivo (para main.py) ou um objeto de arquivo (para api.py).
        """
        read_params = {'encoding': encoding}
        
        if header_option == 'none':
            # Teste 3: Sem cabeçalho. Lê sem cabeçalho e atribui nomes genéricos (A, B, C...)
            read_params['header'] = None
            df = pd.read_csv(source, **read_params)
            # Gera nomes de colunas genéricos
            df.columns = [chr(65 + i) for i in range(len(df.columns))]
        elif header_option == 'generic':
            # Teste 2: Cabeçalho genérico (A, B, C...). Lê a primeira linha como cabeçalho.
            read_params['header'] = 0
            df = pd.read_csv(source, **read_params)
        else: # 'infer' (padrão)
            # Teste 1: Cabeçalho normal. Pandas infere da primeira linha.
            read_params['header'] = 'infer'
            df = pd.read_csv(source, **read_params)
        
        return df

    @staticmethod
    def read_csv_data(file_stream, header_option: str = 'infer'):
        """
        Lê dados CSV de um stream/objeto de arquivo (usado pela API).
        Tenta ler com UTF-8 e depois com Latin-1.
        """
        try:
            # Tenta ler com a codificação primária
            return FileHandler._process_csv(file_stream, header_option, 'utf-8')
        except UnicodeDecodeError:
            logger.warning(f"Falha ao ler stream com utf-8, tentando com latin-1.")
            # Tenta latin-1, comum em dados do governo BR
            file_stream.seek(0) # Volta ao início do stream
            return FileHandler._process_csv(file_stream, header_option, 'latin-1')
        except Exception as e:
            logger.error(f"Erro ao ler stream de CSV: {e}")
            raise

    @staticmethod
    def load_csv(filepath: str, header_option: str = 'infer'):
        """
        Carrega um arquivo CSV a partir de um caminho de arquivo (usado pelo main.py).
        Tenta ler com UTF-8 e depois com Latin-1.
        """
        try:
            return FileHandler._process_csv(filepath, header_option, 'utf-8')
        except UnicodeDecodeError:
            logger.warning(f"Falha ao ler {filepath} com utf-8, tentando com latin-1.")
            return FileHandler._process_csv(filepath, header_option, 'latin-1')
        except Exception as e:
            logger.error(f"Erro ao ler arquivo CSV {filepath}: {e}")
            raise

    @staticmethod
    def save_text(filepath: str, content: str):
        """Salva conteúdo de texto em um arquivo."""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
        except IOError as e:
            logger.error(f"Erro ao salvar arquivo em {filepath}: {e}")