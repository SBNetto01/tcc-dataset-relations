import pandas as pd
import os
import random
import uuid

# --- Configurações ---
NUMERO_DE_LINHAS = 50000
output_dir = 'datasets_teste_grande'

# --- Geração dos Dados Mestres ---
print(f"Gerando {NUMERO_DE_LINHAS} registros de dados sintéticos. Isso pode levar um momento...")

# Gerar dados sintéticos garantindo unicidade
# Nomes são gerados com duplicações propositais para simular dados reais
nomes = [f"Nome_{i % 1000}" for i in range(NUMERO_DE_LINHAS)]
sobrenomes = [f"Sobrenome_{i % 1500}" for i in range(NUMERO_DE_LINHAS)]
nomes_completos = [f"{n} {s}" for n, s in zip(nomes, sobrenomes)]

# Gera identificadores únicos usando UUID para garantir que não haja colisões
cpfs = [str(uuid.uuid4())[:14].replace('-', '.') for _ in range(NUMERO_DE_LINHAS)] # Formato similar a CPF
rgs = [str(uuid.uuid4())[:12].replace('-', '.') for _ in range(NUMERO_DE_LINHAS)]  # Formato similar a RG

# Gera matrículas sequenciais e as embaralha
matriculas = [f"2025{i+1:06d}" for i in range(NUMERO_DE_LINHAS)]
random.shuffle(matriculas)

# Cria o DataFrame mestre que garante a consistência entre as tabelas
data = {
    'nome': nomes_completos,
    'cpf': cpfs,
    'rg': rgs,
    'matricula': matriculas
}
df_master = pd.DataFrame(data)

print("Dados mestres gerados. Criando as tabelas...")

# --- Criação das Três Tabelas ---

# Tabela 1: Dados principais da pessoa/aluno
tabela_principal = df_master[['nome', 'cpf', 'matricula']]

# Tabela 2: Sistema federal, ligando RG e CPF
tabela_federal = df_master[['rg', 'cpf']]

# Tabela 3: Sistema acadêmico, ligando Matrícula e RG
tabela_academica = df_master[['matricula', 'rg']]

# --- Salvar os arquivos em formato CSV ---
os.makedirs(output_dir, exist_ok=True)

tabela_principal_path = os.path.join(output_dir, 'tabela_principal_grande.csv')
tabela_federal_path = os.path.join(output_dir, 'tabela_federal_grande.csv')
tabela_academica_path = os.path.join(output_dir, 'tabela_academica_grande.csv')

tabela_principal.to_csv(tabela_principal_path, index=False)
tabela_federal.to_csv(tabela_federal_path, index=False)
tabela_academica.to_csv(tabela_academica_path, index=False)

print("\nArquivos de teste em larga escala criados com sucesso!")
print(f"Diretório: '{output_dir}'")
print(f"Total de linhas por arquivo: {NUMERO_DE_LINHAS}")
print(f"- {tabela_principal_path}")
print(f"- {tabela_federal_path}")
print(f"- {tabela_academica_path}")