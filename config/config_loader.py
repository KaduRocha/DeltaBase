import yaml
import logging

# -----------------------------------------
# Carrega um arquivo de configuração YAML e o converte em um dicionário Python.
# -----------------------------------------
def load_config(path="config/config.yaml"):
    """
    Parâmetros:
    ----------
    path : str, opcional
        Caminho para o arquivo de configuração YAML. O padrão é 'config/config.yaml'.

    Retorna:
    -------
    dict
        Dicionário contendo as configurações carregadas do arquivo YAML.

    Exceções:
    --------
    Levanta erro se o arquivo não existir ou se o YAML estiver mal formatado.
    """
    try:
        with open(path, "r", encoding="utf-8") as file:
            config = yaml.safe_load(file)
        logging.info(f"Configuração carregada com sucesso: {path}")
        return config
    except FileNotFoundError:
        logging.error(f"Arquivo de configuração não encontrado: {path}")
        raise
    except yaml.YAMLError as e:
        logging.error(f"Erro ao analisar o YAML ({path}): {e}")
        raise
