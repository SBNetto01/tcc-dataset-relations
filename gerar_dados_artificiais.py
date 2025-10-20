import pandas as pd
import os
from faker import Faker
import random

# Inicializa o Faker para dados em português
fake = Faker('pt_BR')

# --- Geração dos Dados Base (100 registros) ---
print("Gerando 100 registros de dados base...")
alunos_data = []
for i in range(100):
    alunos_data.append({
        'matricula-aluno': f"2025{i+1:04d}",
        'nome': fake.name(),
        'email': fake.email(),
        'CPF': fake.unique.cpf(),
        'RG': fake.unique.rg(),
        'data-nascimento': fake.date_of_birth(minimum_age=18, maximum_age=30).strftime('%Y-%m-%d')
    })

disciplinas_data = [
    {'codigo-disciplina': 'INF1001', 'nome-disciplina': 'Algoritmos e Estruturas de Dados', 'departamento': 'Informatica'},
    {'codigo-disciplina': 'MAT1002', 'nome-disciplina': 'Calculo II', 'departamento': 'Matematica'},
    {'codigo-disciplina': 'FIS1003', 'nome-disciplina': 'Fisica Basica I', 'departamento': 'Fisica'},
    {'codigo-disciplina': 'QUI1004', 'nome-disciplina': 'Quimica Geral', 'departamento': 'Quimica'},
]

# --- Criação dos DataFrames Principais ---
df_aluno = pd.DataFrame(alunos_data)
df_disciplina = pd.DataFrame(disciplinas_data)

# --- Listas de Chaves para FKs ---
lista_matriculas = df_aluno['matricula-aluno']
lista_cpfs = df_aluno['CPF']
lista_rgs = df_aluno['RG']
lista_cod_disciplinas = df_disciplina['codigo-disciplina']
lista_nome_disciplinas = df_disciplina['nome-disciplina']

print("Gerando tabelas de relacionamento (100 linhas cada)...")

# --- CORREÇÃO DA LÓGICA DAS TABELAS DE RELACIONAMENTO ---

# Tabela MATRICULA (100 linhas)
# Um aluno (matricula) pode se matricular em várias disciplinas (codigo)
df_matricula = pd.DataFrame({
    'matricula-aluno': [random.choice(lista_matriculas) for _ in range(100)],
    'codigo-disciplina': [random.choice(lista_cod_disciplinas) for _ in range(100)]
})
# Remove duplicatas exatas (mesmo aluno na mesma disciplina)
df_matricula = df_matricula.drop_duplicates().reset_index(drop=True)
print(f"Tabela MATRICULA gerada com {len(df_matricula)} linhas únicas.")

# Tabela CARRO (100 linhas)
# Uma pessoa (CPF) pode ter vários carros (placa)
df_carro = pd.DataFrame({
    'placa': [fake.unique.license_plate() for _ in range(100)],
    'CPF': [random.choice(lista_cpfs) for _ in range(100)],
    'data-aquisição': [fake.date_between(start_date='-5y').strftime('%Y-%m-%d') for _ in range(100)]
})
print(f"Tabela CARRO gerada com {len(df_carro)} linhas.")

# Tabela PRESENÇA (100 linhas)
# Um aluno (RG) pode ter presença em várias disciplinas (nome-disciplina)
df_presenca = pd.DataFrame({
    'RG': [random.choice(lista_rgs) for _ in range(100)],
    'nome-disciplina': [random.choice(lista_nome_disciplinas) for _ in range(100)]
})
# Remove duplicatas exatas (mesmo aluno na mesma disciplina)
df_presenca = df_presenca.drop_duplicates().reset_index(drop=True)
print(f"Tabela PRESENÇA gerada com {len(df_presenca)} linhas únicas.")


# --- Geração dos Arquivos CSV ---

# Teste 1: Com cabeçalhos normais
output_dir_t1 = 'datasets_teste1_normais'
os.makedirs(output_dir_t1, exist_ok=True)
df_aluno.to_csv(f'{output_dir_t1}/ALUNO.csv', index=False)
df_disciplina.to_csv(f'{output_dir_t1}/DISCIPLINA.csv', index=False)
df_matricula.to_csv(f'{output_dir_t1}/MATRICULA.csv', index=False)
df_carro.to_csv(f'{output_dir_t1}/CARRO.csv', index=False)
df_presenca.to_csv(f'{output_dir_t1}/PRESENCA.csv', index=False)
print(f"Teste 1 (cabeçalhos normais) gerado em '{output_dir_t1}'")

# Teste 2: Com cabeçalhos genéricos (A, B, C...)
output_dir_t2 = 'datasets_teste2_genericos'
os.makedirs(output_dir_t2, exist_ok=True)
for name, df in {'ALUNO': df_aluno, 'DISCIPLINA': df_disciplina, 'MATRICULA': df_matricula, 'CARRO': df_carro, 'PRESENÇA': df_presenca}.items():
    df_copy = df.copy()
    df_copy.columns = [chr(65 + i) for i in range(len(df.columns))]
    df_copy.to_csv(f'{output_dir_t2}/{name}.csv', index=False)
print(f"Teste 2 (cabeçalhos genéricos) gerado em '{output_dir_t2}'")

# Teste 3: Sem cabeçalho
output_dir_t3 = 'datasets_teste3_sem_cabecalho'
os.makedirs(output_dir_t3, exist_ok=True)
for name, df in {'ALUNO': df_aluno, 'DISCIPLINA': df_disciplina, 'MATRICULA': df_matricula, 'CARRO': df_carro, 'PRESENÇA': df_presenca}.items():
    df.to_csv(f'{output_dir_t3}/{name}.csv', index=False, header=False)
print(f"Teste 3 (sem cabeçalho) gerado em '{output_dir_t3}'")

print("\nGeração de dados artificiais concluída com sucesso!")