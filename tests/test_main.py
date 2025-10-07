import subprocess
import os
import pytest

def test_main_execution(tmp_path):
    # Cria arquivos CSV de teste temporários
    dataset1 = tmp_path / "dataset1.csv"
    dataset2 = tmp_path / "dataset2.csv"
    output_file = tmp_path / "sugestoes.txt"

    dataset1.write_text("ID,cpf,email\n1,12345678900,ana@email.com\n2,23456789011,bruno@email.com")
    dataset2.write_text("ClienteID,documento,contato\n10,98765432100,ana@email.com\n20,87654321099,bruna@email.com")

    # Executa o script principal usando subprocess
    result = subprocess.run(
        [
            "python", "main.py",
            str(dataset1),
            str(dataset2),
            "-o", str(output_file),
            "-t", "70"
        ],
        capture_output=True,
        text=True
    )

    # Verifica se a execução foi bem-sucedida
    assert result.returncode == 0
    assert output_file.exists()

    # Verifica o conteúdo do arquivo de saída
    output_content = output_file.read_text()
    assert "email" in output_content or "cpf" in output_content or "contato" in output_content

