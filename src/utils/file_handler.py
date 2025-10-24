# Em: src/utils/file_handler.py
import pandas as pd
import os
import logging
from io import StringIO, BytesIO # Adicionado para manipulação de streams
from typing import Optional # <<< ADICIONADO

# Assume que LOGGER_NAME está definido em algum lugar ou use 'DataRelationFinder'
try:
    from .logger import LOGGER_NAME
except ImportError:
    LOGGER_NAME = 'DataRelationFinder'

logger = logging.getLogger(LOGGER_NAME)

class FileHandler:

    @staticmethod
    def _try_read_csv(source, header_option: str, encoding: str, delimiter: str):
        """Tenta ler o CSV com uma configuração específica, pulando linhas ruins."""
        read_params = {
            'encoding': encoding,
            'sep': delimiter,
            'on_bad_lines': 'warn' # Ou 'skip'. 'warn' avisa no log, 'skip' ignora silenciosamente.
                                    # Escolha 'warn' para depuração inicial.
        }
        logger.debug(f"Tentando pd.read_csv com parâmetros: {read_params}")

        # Guarda a posição original se for um stream
        original_position = None
        if hasattr(source, 'seek'):
            original_position = source.tell()

        try:
            if header_option == 'none':
                read_params['header'] = None
                df = pd.read_csv(source, **read_params)
                # Gera nomes de colunas genéricos apenas se o DataFrame não estiver vazio
                if not df.empty:
                    df.columns = [f"col_{i}" for i in range(len(df.columns))] # Nomes mais explícitos
            elif header_option == 'generic':
                read_params['header'] = 0
                df = pd.read_csv(source, **read_params)
            else: # 'infer'
                read_params['header'] = 'infer'
                df = pd.read_csv(source, **read_params)

            logger.info(f"Leitura bem-sucedida com encoding='{encoding}', sep='{delimiter}'. Shape: {df.shape if df is not None else 'N/A'}")
            return df

        except pd.errors.EmptyDataError:
            logger.warning(f"Arquivo/Stream vazio ou sem colunas com sep='{delimiter}'.")
            # Retorna um DataFrame vazio em vez de falhar
            return pd.DataFrame()
        except Exception as e:
            logger.warning(f"Falha na tentativa de leitura com {read_params}: {e}")
            # Reseta a posição do stream se deu erro, para a próxima tentativa
            if original_position is not None and hasattr(source, 'seek'):
                source.seek(original_position)
            raise # Relança a exceção para ser pega no loop de fallbacks

    @staticmethod
    def _read_csv_with_fallbacks(source, header_option: str, separator: Optional[str] = None): # <<< PARÂMETRO ADICIONADO
        """Tenta ler CSV com diferentes delimitadores e codificações."""
        encodings_to_try = ['utf-8', 'latin-1']
        
        # --- LÓGICA DO SEPARADOR ATUALIZADA ---
        if separator:
            # Se um separador foi FORNECIDO, SÓ tenta ele.
            delimiters_to_try = [separator]
            logger.info(f"Usando separador FORNECIDO: '{separator}'")
        else:
            # Se não foi fornecido, usa a lógica de fallback.
            delimiters_to_try = [';', ','] # Tenta ponto e vírgula PRIMEIRO, depois vírgula
            logger.info("Nenhum separador fornecido. Usando fallback: [';', ',']")
        # --- FIM DA LÓGICA ATUALIZADA ---

        last_exception = None
        source_repr = repr(source) # Para logging

        for encoding in encodings_to_try:
            for delimiter in delimiters_to_try:
                try:
                    # Se 'source' for um stream, resetamos a cada tentativa REAL de leitura
                    if hasattr(source, 'seek'):
                        source.seek(0)

                    logger.info(f"Tentando ler {source_repr} com encoding='{encoding}' e sep='{delimiter}'...")
                    df = FileHandler._try_read_csv(source, header_option, encoding, delimiter)

                    # --- VERIFICAÇÃO CRÍTICA ADICIONADA ---
                    # Se a leitura "bem-sucedida" (sem exceção) resultar em 1 coluna,
                    # E o separador NÃO foi forçado pelo usuário (ou seja, foi o fallback)
                    # E o separador era ';', então provavelmente está errado.
                    if df is not None and len(df.columns) == 1 and not separator and delimiter == ';':
                        logger.warning(f"Leitura com sep=';' resultou em 1 coluna. Ignorando e tentando próximo delimitador (',').")
                        last_exception = Exception("Leitura com ';' resultou em 1 coluna.")
                        continue # Pula para a próxima tentativa (vírgula)
                    # --- FIM DA VERIFICAÇÃO ---

                    if df is not None:
                        # Removido o log duplicado de sucesso daqui, já está em _try_read_csv
                        return df # Retorna o DataFrame na primeira leitura bem-sucedida

                except UnicodeDecodeError as ude:
                    logger.warning(f"Falha de encoding com '{encoding}' para {source_repr}. Tentando próximo encoding...")
                    last_exception = ude
                    break # Pula para o próximo encoding
                except Exception as e:
                    logger.warning(f"Falha ao ler {source_repr} com encoding='{encoding}' e sep='{delimiter}': {e}")
                    last_exception = e
                    # Continua para tentar o próximo delimitador/encoding

        # Se chegou aqui, todas as tentativas falharam
        logger.error(f"Não foi possível ler {source_repr} após tentar combinações. Último erro: {last_exception}")
        # Retorna DataFrame vazio em vez de levantar erro para não parar a API? Ou levanta?
        # Decisão: Levantar erro para a API saber que falhou.
        raise ValueError(f"Não foi possível ler o arquivo CSV {source_repr}. Último erro: {last_exception}") from last_exception


    @staticmethod
    def read_csv_data(file_stream, header_option: str = 'infer', separator: Optional[str] = None): # <<< PARÂMETRO ADICIONADO
        """Lê dados CSV de um stream/objeto de arquivo (usado pela API)."""
        # Garante que temos um stream de bytes que pode ser lido várias vezes
        try:
            # Lê todo o conteúdo na memória
            content = file_stream.read()
            # Cria um BytesIO que pode ser "rebobinado" (seek)
            bytes_stream = BytesIO(content)
            return FileHandler._read_csv_with_fallbacks(bytes_stream, header_option, separator) # <<< PARÂMETRO PASSADO
        except Exception as e:
            logger.error(f"Erro ao preparar stream para leitura: {e}")
            raise

    @staticmethod
    def load_csv(filepath: str, header_option: str = 'infer', separator: Optional[str] = None): # <<< PARÂMETRO ADICIONADO
        """Carrega um arquivo CSV a partir de um caminho de arquivo (usado pelo main.py)."""
        if not os.path.exists(filepath):
            logger.error(f"Arquivo não encontrado: {filepath}")
            raise FileNotFoundError(f"Arquivo não encontrado: {filepath}")
        # Passa o filepath diretamente, _read_csv_with_fallbacks lida com isso
        return FileHandler._read_csv_with_fallbacks(filepath, header_option, separator) # <<< PARÂMETRO PASSADO

    @staticmethod
    def save_text(filepath: str, content: str):
        """Salva conteúdo de texto em um arquivo."""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
        except IOError as e:
            logger.error(f"Erro ao salvar arquivo em {filepath}: {e}")