import pandas as pd

def compare_data(df1, df2, key, ignore_columns=None):
    keys = [k.strip() for k in key.split(",")]

    for k in keys:
        if k not in df1.columns or k not in df2.columns:
            raise ValueError(f"Erro: coluna-chave '{k}' não encontrada em ambos os arquivos.\n"
                             f"Colunas disponíveis em A: {list(df1.columns)}\n"
                             f"Colunas disponíveis em B: {list(df2.columns)}")

    df1.set_index(keys, inplace=True)
    df2.set_index(keys, inplace=True)

    only_in_df1 = df1[~df1.index.isin(df2.index)].reset_index()
    only_in_df2 = df2[~df2.index.isin(df1.index)].reset_index()

    common_keys = df1.index.intersection(df2.index)
    diffs = []

    for k in common_keys:
        row1 = df1.loc[k]
        row2 = df2.loc[k]
        if isinstance(row1, pd.DataFrame) or isinstance(row2, pd.DataFrame):
            continue

        r1 = row1.drop(ignore_columns, errors='ignore') if ignore_columns else row1
        r2 = row2.drop(ignore_columns, errors='ignore') if ignore_columns else row2

        diff_fields = {}
        for col in r1.index:
            val1 = r1[col]
            val2 = r2[col]
            if val1 != val2:
                diff_fields[col] = {"df1": val1, "df2": val2}

        if diff_fields:
            diffs.append({"key": k, "df1": r1.to_dict(), "df2": r2.to_dict(), "differences": diff_fields})


    return only_in_df1, only_in_df2, diffs
