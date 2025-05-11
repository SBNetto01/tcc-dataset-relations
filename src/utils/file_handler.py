import pandas as pd

class FileHandler:
    """
    Classe utilitária para lidar com operações de leitura e escrita de arquivos.
    """

    @staticmethod
    def load_csv(filepath: str) -> pd.DataFrame:
        """
        Carrega um arquivo CSV como um DataFrame do pandas.

        Args:
            filepath (str): Caminho para o arquivo CSV.

        Returns:
            pd.DataFrame: DataFrame carregado.
        """
        try:
            return pd.read_csv(filepath)
        except Exception as e:
            raise IOError(f"Erro ao carregar o arquivo {filepath}: {e}")

    @staticmethod
    def save_text(filepath: str, content: str):
        """
        Salva um conteúdo de texto em um arquivo.

        Args:
            filepath (str): Caminho para o arquivo de destino.
            content (str): Texto a ser salvo.
        """
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
        except Exception as e:
            raise IOError(f"Erro ao salvar o arquivo {filepath}: {e}")
