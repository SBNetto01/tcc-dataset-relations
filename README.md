# tcc-dataset-relations
Projeto de TCC de automatização de relações entre datasets

Possíveis requisitos do programa: Atualizar constantemente

1. Requisitos Funcionais (RF)
Os requisitos funcionais descrevem as funcionalidades que o sistema deve oferecer.

RF-01: Importação de Datasets
📌 O sistema deve permitir a importação de datasets nos formatos CSV, JSON e SQL.
Critérios de Aceitação:

O usuário pode selecionar e carregar múltiplos arquivos CSV e JSON.

O usuário pode conectar um banco de dados SQL e selecionar tabelas específicas.

O sistema deve validar a estrutura dos arquivos para garantir que sejam carregados corretamente.

RF-02: Perfilamento dos Dados
📌 O sistema deve analisar a estrutura de cada dataset importado e gerar metadados sobre ele.
Critérios de Aceitação:

O sistema deve identificar e exibir:

Nome das colunas.

Tipo de dado de cada coluna.

Contagem de valores únicos.

Contagem de valores nulos.

O sistema deve armazenar esse perfilamento para referência futura.

RF-03: Detecção de Similaridade entre Atributos
📌 O sistema deve identificar atributos similares entre diferentes datasets.
Critérios de Aceitação:

O sistema deve comparar colunas com base em:

Nome (similaridade textual).

Tipo de dado.

Distribuição de valores.

O sistema deve gerar um score de similaridade para cada par de colunas comparadas.

O usuário deve visualizar uma lista das possíveis colunas correspondentes.

RF-04: Identificação de Possíveis Relações entre Datasets
📌 O sistema deve sugerir relações entre datasets, incluindo chaves estrangeiras implícitas.
Critérios de Aceitação:

O sistema deve verificar se os valores de uma coluna candidata a chave estrangeira estão presentes em uma possível chave primária.

O sistema deve apresentar as relações identificadas com um nível de confiança baseado na análise dos dados.

RF-05: Validação das Relações Detectadas
📌 O sistema deve permitir que o usuário valide as relações detectadas.
Critérios de Aceitação:

O sistema deve permitir que o usuário aceite ou rejeite relações sugeridas.

O usuário pode visualizar estatísticas sobre a qualidade da correspondência antes de validar.

RF-06: Ajustes e Harmonização dos Dados
📌 O sistema deve oferecer opções para harmonizar os dados quando houver pequenas discrepâncias.
Critérios de Aceitação:

O sistema deve sugerir transformações, como:

Padronização de formatos (ex.: datas, números).

Remoção de espaços e caracteres especiais.

O usuário pode aceitar ou rejeitar as transformações sugeridas.

RF-07: Geração de Relatórios
📌 O sistema deve gerar um relatório consolidado sobre as relações encontradas.
Critérios de Aceitação:

O relatório deve incluir:

Resumo dos datasets analisados.

Relações identificadas (chaves estrangeiras, similaridades).

Sugestões de combinação (união, interseção, diferença).

O relatório deve ser exportável nos formatos CSV, JSON e Markdown.

2. Requisitos Não Funcionais (RNF)
Os requisitos não funcionais especificam características de qualidade, desempenho e segurança do sistema.

RNF-01: Linguagem e Tecnologias
📌 O sistema deve ser desenvolvido em Python, utilizando bibliotecas para análise de dados.
Critérios de Aceitação:

O código deve utilizar pandas para manipulação de dados.

O código pode usar difflib para análise de similaridade textual.

O sistema pode utilizar sqlite3 ou SQLAlchemy para conexão com bases SQL.

RNF-02: Desempenho e Escalabilidade
📌 O sistema deve ser capaz de processar grandes volumes de dados de forma eficiente.
Critérios de Aceitação:

O tempo de processamento para datasets médios (~100MB) deve ser inferior a 5 minutos.

O sistema deve utilizar técnicas de otimização, como processamento em lote.

RNF-03: Interface e Usabilidade
📌 O sistema deve apresentar uma interface clara para o usuário.
Critérios de Aceitação:

O sistema pode ter uma interface gráfica (ex.: Jupyter Notebook, Streamlit, Dash) ou ser baseado em linha de comando (CLI).

As mensagens de erro devem ser descritivas e indicar como corrigir problemas.

RNF-04: Documentação e Manutenção
📌 O código deve ser bem documentado e seguir boas práticas de desenvolvimento.
Critérios de Aceitação:

Cada função principal deve ter um docstring explicando sua funcionalidade.

O repositório deve conter um arquivo README.md com instruções de uso.

RNF-05: Segurança e Integridade dos Dados
📌 O sistema deve garantir que os dados originais não sejam alterados sem autorização.
Critérios de Aceitação:

O sistema deve sempre trabalhar com cópias dos dados originais.

O usuário deve confirmar antes de aplicar modificações permanentes.