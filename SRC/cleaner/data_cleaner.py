import pandas as pd

from SRC.utils.reader import read_csv_with_schema, save_csv
from SRC.utils.logger import logger


class DataCleaner:
    MONEY_COLS = [
        "order_amount", "coupon_amount", "freight_amount", "payable_amount",
        "unit_price", "actual_amount", "discount_amount", "cost_price",
    ]
    DATE_COLS = ["order_time", "updated_at", "created_at", "register_time"]
    CODE_COLS = [
        "receiver_province_code", "province_code", "shop_id",
        "customer_id", "product_id", "order_id", "order_detail_id",
        "category_id",
    ]

    def check_duplicate(self, df):
        dup_count = df.duplicated().sum()
        if dup_count > 0:
            logger.info(f"去重 {dup_count} 行")
        return df.drop_duplicates().reset_index(drop=True)

    def check_type(self, df):
        for col in self.MONEY_COLS:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")
        for col in self.DATE_COLS:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors="coerce")
        for col in self.CODE_COLS:
            if col in df.columns:
                df[col] = df[col].astype("string").str.strip()
        return df

    def check_fillna(self, df):
        for col in self.MONEY_COLS:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
        return df

    def trim_text(self, df):
        for col in df.columns:
            if df[col].dtype == "object":
                df[col] = df[col].astype(str).str.strip()
        return df

    def clean(self, input_file, output_file, schema):
        logger.info(f"清洗 {input_file}")
        df = read_csv_with_schema(input_file, schema)
        df = self.check_duplicate(df)
        df = self.check_fillna(df)
        df = self.check_type(df)
        df = self.trim_text(df)
        save_csv(df, output_file)
        logger.info(f"清洗完成 {output_file} 行数={len(df)}")
        return df