from src.components.attribute_validator import AttributeValidator
import pandas as pd

df1 = pd.read_csv("data/dataset1.csv")
df2 = pd.read_csv("data/dataset2.csv")

validator = AttributeValidator(df1, df2)
suggestions = validator.suggest_similar_attributes()

for s in suggestions:
    print(s)
