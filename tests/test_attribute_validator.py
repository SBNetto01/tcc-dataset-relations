import os
import sys
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.components.attribute_validator import AttributeValidator

df1 = pd.DataFrame({
    "ID": [1, 2, 3],
    "cpf": ['195.868.392-86', '107.792.984-82', '206.958.464-91'],
    "Email": ["ana@email.com", "bruno@email.com", "carlos@email.com"]
})

df2 = pd.DataFrame({
    "ClienteID": [10, 20, 30],
    "documento": ['540.292.339-65', '202.405.697-76', '309.202.101-32'],
    "contato": ["ana@email.com", "bruna@email.com", "carla@email.com"]
})

validator = AttributeValidator(df1, df2, fuzzy_threshold=70)
suggestions = validator.suggest_similar_attributes()

with open("results/test_suggestions.txt", "w", encoding="utf-8") as f:
    for col1 in df1.columns:
        for col2 in df2.columns:
            comparacao = validator.compare_column_names()
            f.write(f"{col1} x {col2}: {comparacao}\n")

    f.write("\nSugestões finais:\n")
    for s in suggestions:
        f.write(str(s) + "\n")
