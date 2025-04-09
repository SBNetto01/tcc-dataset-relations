import sys
import os
import pandas as pd

# Garante que o caminho do projeto esteja incluído
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.components.attribute_validator import AttributeValidator

# Dados simulados para testar similaridade de conteúdo
df1 = pd.DataFrame({
    "ID": [1, 2, 3],
    "cpf": ['195.868.392-86', '107.792.984-82', '206.958.464-91'],
    "Email": ["ana@gmail.com", "bruno@yahoo.com", "carlos@hotmail.com"]
})

df2 = pd.DataFrame({
    "ClienteID": [2, 1, 3],
    "documento": ['195.008.992-86', '107.552.984-82', '309.202.101-32'],
    "contato": ["ana333@yahoo.com", "bruninhaa@hotmail.com", "carlona@gmail.com"]
})

# Instancia o validador com thresholds ajustados
validator = AttributeValidator(df1, df2, fuzzy_threshold=70, content_threshold=0.5)

# Executa a sugestão de atributos
sugestoes = validator.sugerir_atributos_similares()

# Mostra os resultados finais da sugestão
print("\n=== Sugestões de Atributos Compatíveis ===")
if sugestoes:
    for sugestao in sugestoes:
        print(sugestao)
else:
    print("Nenhuma sugestão encontrada.")