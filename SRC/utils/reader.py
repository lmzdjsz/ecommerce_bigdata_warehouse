import pandas as pd

from SRC.config.settings import CSV_ENCODING


def read_csv_with_schema(file_path, schema=None):
    dtype = schema if schema else None
    return pd.read_csv(
        file_path, dtype=dtype, encoding=CSV_ENCODING, low_memory=False
    )


def save_csv(df, output_file):
    import os
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    df.to_csv(output_file, index=False, encoding=CSV_ENCODING)