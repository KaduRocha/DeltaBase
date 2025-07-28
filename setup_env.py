import os
import logging

# -----------------------------------------
# Configuração básica de logging
# -----------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# -----------------------------------------
# Cria a estrutura básica de diretórios do projeto.
# -----------------------------------------
def criar_pastas():
    """
    Diretórios:
        - config/
        - core/
        - files/input/
        - files/output/
        - files/relatorio/
    """
    pastas = [
        "config",
        "core",
        "files/input",
        "files/output",
        "files/relatorio"
    ]

    for pasta in pastas:
        try:
            os.makedirs(pasta, exist_ok=True)
            logging.info(f"Pasta criada (ou já existia): {pasta}")
        except Exception as e:
            logging.error(f"Não foi possível criar a pasta '{pasta}': {e}")

# -----------------------------------------
# Cria arquivos iniciais do projeto.
# -----------------------------------------
def criar_arquivos_iniciais():
    """
    Cria arquivos iniciais úteis:
        - __init__.py na pasta core/
        - config.yaml vazio na pasta config/
        - .gitkeep nas pastas files para controle de versão
    """

    arquivos = {
        "core/__init__.py": "",
        "config/config.yaml": "# Configuração inicial do projeto\n",
        # "files/input/.gitkeep": "",
        # "files/output/.gitkeep": "",
        # "files/relatorio/.gitkeep": ""
    }

    for caminho, conteudo in arquivos.items():
        if not os.path.exists(caminho):
            try:
                with open(caminho, "w", encoding="utf-8") as f:
                    f.write(conteudo)
                logging.info(f"Arquivo criado: {caminho}")
            except Exception as e:
                logging.error(f"Falha ao criar '{caminho}': {e}")
        else:
            logging.debug(f"Arquivo já existe: {caminho}")

if __name__ == "__main__":
    criar_pastas()
    criar_arquivos_iniciais()
