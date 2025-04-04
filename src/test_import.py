from data_loader import load_csv, load_json, load_sql

#opções de teste de importação
csv_df = load_csv("../datasets/exemplo.csv")
print(csv_df.head())

json_df = load_json("../datasets/exemplo.json")
print(json_df.head())

sql_df = load_sql("../datasets/exemplo.db", "SELECT * FROM tabela_exemplo")
print(sql_df.head())
