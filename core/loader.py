import os
import glob
import pandas as pd
from sqlalchemy import create_engine
from unidecode import unidecode
import chardet
import logging

# -----------------------------------------
# importar o módulo 'chardet', que é usado para detectar automaticamente a codificação de arquivos de texto.
# Se a importação for bem-sucedida, define a flag HAS_CHARDET como True para indicar que a biblioteca está disponível.
# Caso contrário, captura a exceção ImportError e define HAS_CHARDET como False, sinalizando que a funcionalidade de detecção automática não estará disponível.
# -----------------------------------------
try:
    import chardet
    HAS_CHARDET = True
except ImportError:
    HAS_CHARDET = False

# -----------------------------------------
# Setup de logging
# -----------------------------------------
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# -----------------------------------------
# Detecta encoding automaticamente (chardet)
# -----------------------------------------
def detect_encoding(path):
    if not HAS_CHARDET:
        return None
    with open(path, 'rb') as f:
        result = chardet.detect(f.read(10000))
    return result['encoding']

# -----------------------------------------
# Normaliza nomes das colunas (acentos, espaços etc.)
# -----------------------------------------
def normalize_columns(df):
    df.columns = [
        unidecode(col).upper().strip().replace(" ", "_") for col in df.columns
    ]
    return df

# -----------------------------------------
# Exceção personalizada
# -----------------------------------------
class CSVLoadError(Exception):
    pass

# -----------------------------------------
# Carrega arquivo CSV, TXT, TSV ou planilhas Excel
# -----------------------------------------
def load_csv(path, sep, quotechar, encoding=None):
    ext = os.path.splitext(path)[1].lower()
    if ext not in ['.csv', '.txt', '.tsv', '.xls', '.xlsx']:
        raise CSVLoadError(f"\nTipo de arquivo não suportado: {ext} (apenas .csv, .txt, .tsv, .xls, .xlsx)")

    # Codificações a tentar
    encodings_to_try = (
        [encoding] if encoding else ["utf-8", "utf-8-sig", "latin1", "cp1252", "iso-8859-1"]
    )

    # Tenta leitura com múltiplas codificações
    for enc in encodings_to_try:
        try:
            if ext in ['.xls', '.xlsx']:
                df = pd.read_excel(path, dtype=str).fillna("")
            else:
                sep_to_use = sep if ext != '.tsv' else '\t'
                df = pd.read_csv(
                    path,
                    dtype=str,
                    sep=sep_to_use,
                    quotechar=quotechar,
                    encoding=enc,
                    on_bad_lines='skip'
                ).fillna("")
            df = normalize_columns(df)
            logging.info(f"Arquivo carregado com codificação: {enc} | {path}")
            return df
        except Exception as e:
            logging.warning(f"TENTATIVA COM encoding '{enc}' falhou: {e}")
    
    # Tentativa com chardet, se disponível
    if HAS_CHARDET:
        try:
            detected = detect_encoding(path)
            if detected:
                logging.info(f"Tentando encoding detectado: {detected}")
                df = pd.read_csv(path, dtype=str, sep=sep, quotechar=quotechar, encoding=detected).fillna("")
                df = normalize_columns(df)
                logging.info(f"Arquivo carregado com encoding detectado: {detected} | {path}")
                return df
        except Exception as e:
            logging.warning(f"Falha ao usar encoding detectado por chardet: {e}")

    raise CSVLoadError(f"\nNão foi possível carregar o arquivo {path} com as codificações testadas.")

# -----------------------------------------
# Carrega tabela de banco de dados com SQLAlchemy
# -----------------------------------------
def load_sql_table(conn_str, table_name):
    try:
        engine = create_engine(conn_str)
        df = pd.read_sql_table(table_name, engine).astype(str).fillna("")
        df = normalize_columns(df)
        logging.info(f"Tabela '{table_name}' carregada do banco de dados.")
        return df
    except Exception as e:
        raise CSVLoadError(f"Erro ao carregar tabela {table_name} do banco de dados: {e}")

# -----------------------------------------
# Expande padrão de arquivos (diretórios, *.csv etc.)
# -----------------------------------------
def expand_file_list(path_pattern):
    if os.path.isdir(path_pattern):
        files = sorted(
            glob.glob(os.path.join(path_pattern, "*.csv")) +
            glob.glob(os.path.join(path_pattern, "*.txt")) +
            glob.glob(os.path.join(path_pattern, "*.tsv")) +
            glob.glob(os.path.join(path_pattern, "*.xls")) +
            glob.glob(os.path.join(path_pattern, "*.xlsx"))
        )
        logging.info(f"{len(files)} arquivos encontrados em: {path_pattern}")
        return files
    elif os.path.isfile(path_pattern):
        logging.info(f"Arquivo único detectado: {path_pattern}")
        return [path_pattern]
    else:
        files = sorted(glob.glob(path_pattern))
        if not files:
            logging.warning(f"Nenhum arquivo encontrado com padrão: {path_pattern}")
        return files
