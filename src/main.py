import os
import pandas as pd
from components.data_profiler import DataProfiler
from components.attribute_validator import AttributeValidator

# Carregar datasets fornecidos
df1 = pd.read_csv("datasets/Advanced.csv")
df2 = pd.read_csv("datasets/Player Play By Play.csv")

# Perfilamento de dados
profiler1 = DataProfiler(df1)
profiler2 = DataProfiler(df2)

print("==== Perfil do Dataset: Advanced.csv ====")
print(profiler1.generate_profile())

print("\n==== Perfil do Dataset: Player Play By Play.csv ====")
print(profiler2.generate_profile())

# Comparação entre atributos
validator = AttributeValidator(df1, df2, fuzzy_threshold=70)
suggestions = validator.suggest_similar_attributes()

# Salvar sugestões
os.makedirs("results", exist_ok=True)
with open("results/attribute_suggestions.txt", "w", encoding="utf-8") as f:
    f.write("==== Sugestões de Atributos Compatíveis ====\n\n")
    for suggestion in suggestions:
        f.write(str(suggestion) + "\n")

print("\nSugestões salvas em 'results/attribute_suggestions.txt'")
