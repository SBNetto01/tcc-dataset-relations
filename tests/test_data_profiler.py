import pandas as pd
from src.components.data_profiler import DataProfiler

df = pd.DataFrame({
    "ID": [1, 2, 3],
    "Nome": ["Ana", "Bruno", "Carlos"],
    "Idade": [25, 30, 22],
    "Salário": [3000, 4000, 3500]
})

profiler = DataProfiler(df)
profile = profiler.generate_profile()

print("==== Teste do Data Profiler ====")
print(profile)
