import os
import pandas as pd
import logging
from core.loader import load_csv, load_sql_table, expand_file_list, CSVLoadError
from core.comparator import compare_data
from core.report import gerar_relatorio, save_to_db
from config.config_loader import load_config

# -----------------------------------------
# Carrega os dados de uma fonte configurada, que pode ser um banco de dados ou um arquivo CSV.
# -----------------------------------------
def carregar_fonte(fonte_config):
    """
    Parâmetros:
    - fonte_config (dict): Dicionário contendo as configurações da fonte de dados. Deve incluir:
        - 'type': 'database' ou outro (assumido como arquivo)
        - 'conn_str' e 'table' (para banco de dados)
        - 'path', 'sep', 'quotechar', 'encoding' (para CSV)

    Retorna:
    - pandas.DataFrame: DataFrame contendo os dados carregados da fonte.
    """
    if fonte_config['type'] == 'database':
        logging.info(f"Carregando tabela {fonte_config['table']} do banco")
        return load_sql_table(fonte_config['conn_str'], fonte_config['table'])
    else:
        path = expand_file_list(fonte_config['path'])[0]
        logging.info(f"Carregando arquivo {path}")
        return load_csv(path, fonte_config.get('sep', ';'), fonte_config.get('quotechar', '"'), fonte_config.get('encoding'))

# -----------------------------------------
# Função principal que executa todo o fluxo de comparação de dados entre duas fontes (banco ou arquivos).
# -----------------------------------------
def main():
    """
    Etapas executadas:
    1. Garante a existência dos diretórios de saída.
    2. Carrega as configurações do processo a partir de um arquivo YAML.
    3. Carrega os dados das fontes A e B (banco ou arquivo CSV).
    4. Define as chaves de comparação e colunas a serem ignoradas.
    5. Verifica se os dados estão disponíveis.
    6. Realiza a comparação entre os dados das fontes A e B.
    7. Gera um relatório das diferenças encontradas.
    8. (Opcional) Salva o relatório em um banco de dados.
    9. Registra logs para cada etapa do processo.

    Exceções tratadas:
    - CSVLoadError: falhas específicas na carga de dados.
    - Exception: erros inesperados.
    """
    OUTPUT_DIR = "files/output"
    REPORT_DIR = "files/relatorio"

    try:
        # Garantir que os diretórios existam
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        os.makedirs(REPORT_DIR, exist_ok=True)
        
        # Carrega o arquivo de configuração YAML contendo parâmetros e caminhos
        config = load_config()

        df_a = carregar_fonte(config['source_a'])
        df_b = carregar_fonte(config['source_b'])

        # Extrai a(s) coluna(s) chave(s) para comparação e colunas a ignorar
        key = config['comparison']['key']
        if isinstance(key, list):
            # Se for lista, converte para string separada por vírgula
            key_str = ",".join(key)
        else:
            key_str = key

        ignore_columns = [
            col.strip().upper() for col in config['comparison'].get('ignore_columns', [])
        ]

        if df_a.empty or df_b.empty:
            logging.warning("Uma das fontes está vazia. Abortando.")
            return

        # Realiza a comparação entre os DataFrames carregados
        only_a, only_b, diffs = compare_data(df_a, df_b, key_str, ignore_columns)

        # Loga um resumo do resultado da comparação
        logging.info("Resumo:")
        logging.info(f"Somente A: {len(only_a)}, Somente B: {len(only_b)}, Divergentes: {len(diffs)}")

        # Define o caminho do arquivo de relatório e gera o arquivo
        report_path = os.path.join(REPORT_DIR, config['report'].get('output_file', 'relatorio_diff.csv'))
        gerar_relatorio(only_a, only_b, diffs, report_path)

        # Se configurado, salva o relatório no banco de dados
        if config['report'].get('save_to_db'):
            relatorio_df = pd.DataFrame({
                "key": [str(d["key"]) for d in diffs],
                "fonte_a": [str(d["df1"]) for d in diffs],
                "fonte_b": [str(d["df2"]) for d in diffs]
            })
            save_to_db(
                relatorio_df,
                config['report']['db_url'],
                config['report']['db_table']
            )

    except CSVLoadError as e:
        # Log de erro específico para falha na carga de arquivos/tabelas
        logging.error(f"Erro na carga: {e}")
    except Exception as e:
        # Log para erros inesperados gerais
        logging.error(f"Erro inesperado: {e}")

# Executa o main quando o script é chamado diretamente
if __name__ == "__main__":
    main()
