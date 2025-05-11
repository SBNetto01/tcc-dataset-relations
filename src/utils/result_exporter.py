import os

def export_results_to_txt(suggestions, filename):
    result_path = os.path.join(os.path.dirname(__file__), '..', '..', filename)
    with open(result_path, 'w', encoding='utf-8') as file:
        if not suggestions:
            file.write("Nenhuma sugestão encontrada.")
        else:
            for s in suggestions:
                linha = f"{s['Coluna Dataset 1']} x {s['Coluna Dataset 2']} ({s['Tipo']}) -> {s['Tipo de Similaridade']}\n"
                file.write(linha)
