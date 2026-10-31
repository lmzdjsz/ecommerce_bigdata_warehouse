from SRC.utils.reader import read_csv_with_schema, save_csv


class BaseBuilder:
    def read(self, file, schema=None):
        return read_csv_with_schema(file, schema)

    def save(self, df, output_file):
        save_csv(df, output_file)