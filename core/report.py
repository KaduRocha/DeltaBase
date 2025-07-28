import os
import pandas as pd
import logging
from sqlalchemy import create_engine

# -----------------------------------------
# Setup de logging
# -----------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# -----------------------------------------
# Função que salva um DataFrame em uma tabela de banco de dados usando SQLAlchemy
# -----------------------------------------
def save_to_db(df, conn_str, table_name):
    try:
        engine = create_engine(conn_str)
        df.to_sql(table_name, engine, if_exists='replace', index=False)
        logging.info(f"Relatório salvo na tabela '{table_name}' do banco de dados com sucesso.")
    except Exception as e:
        logging.error(f"Erro ao salvar no banco de dados: {e}")

# -----------------------------------------
# Função que gera um relatório de diferenças entre duas fontes de dados
# -----------------------------------------
def gerar_relatorio(only_a, only_b, diffs, filename="relatorio_comparativo.txt", pasta_saida="files/relatorio"):
    # Função interna para formatar a chave primária, caso seja tupla
    def format_key(k):
        if isinstance(k, tuple):
            return ', '.join(str(i) for i in k)
        return str(k)

    # Verifica se há alguma diferença para relatar
    if only_a.empty and only_b.empty and not diffs:
        logging.warning("Nenhuma diferença encontrada. Relatório não será gerado.")
        return

    # Cria o diretório de saída, se não existir
    os.makedirs(pasta_saida, exist_ok=True)

    # Garante que apenas o nome do arquivo (sem caminhos) será usado, evitando conflitos
    filename = os.path.basename(filename)
    # Constrói o caminho completo do arquivo de saída dentro da pasta especificada.
    out_path = os.path.join(pasta_saida, filename)

    try:
        # Abre o arquivo para escrita do relatório
        with open(out_path, "w", encoding="utf-8") as f:
            # Escreve os registros exclusivos da fonte A
            f.write("### Registros somente na Fonte A:\n")
            f.write(only_a.to_csv(index=False))
            f.write("\n\n### Registros somente na Fonte B:\n")
            f.write(only_b.to_csv(index=False))
            f.write("\n\n### Registros diferentes com mesma chave:\n")
            
            # Escreve as diferenças entre registros com mesma chave
            for d in diffs:
                chave_formatada = format_key(d['key'])
                f.write(f"Chave: {chave_formatada}\n")
                f.write(f"Diferenças:\n")
                for campo, valores in d['differences'].items():
                    f.write(f" - {campo}: Fonte A = '{valores['df1']}', Fonte B = '{valores['df2']}'\n")
                f.write("\n")
        logging.info(f"Relatório salvo em: {out_path}")
    except Exception as e:
        logging.error(f"Erro ao gerar relatório: {e}")
