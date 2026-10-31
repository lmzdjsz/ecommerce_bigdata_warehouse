import pandas as pd

from SRC.warehouse.base_builder import BaseBuilder
from SRC.config.settings import TECH_COLUMNS
from SRC.config.schema import DWD_ORDER_COLUMNS
from SRC.utils.logger import logger


class DWDBuilder(BaseBuilder):
    def build_order_detail(
        self, order_file, order_detail_file,
        customer_file, product_file, output_file,
    ):
        logger.info("构建 DWD 明细宽表")
        order_df = self.read(order_file)
        detail_df = self.read(order_detail_file)
        customer_df = self.read(customer_file)
        product_df = self.read(product_file)

        for df in [order_df, detail_df, customer_df, product_df]:
            df.drop(columns=TECH_COLUMNS, errors="ignore", inplace=True)

        orphan_detail = (~detail_df["order_id"].isin(order_df["order_id"])).sum()
        missing_customer = (~order_df["customer_id"].isin(customer_df["customer_id"])).sum()
        missing_product = (~detail_df["product_id"].isin(product_df["product_id"])).sum()
        logger.info(
            f"关联预检: 孤立明细={orphan_detail}, 缺客户={missing_customer}, 缺商品={missing_product}"
        )

        df = order_df.merge(detail_df, on="order_id", how="left", validate="one_to_many")
        df = df.merge(
            customer_df, on="customer_id", how="left", validate="many_to_one",
            suffixes=("", "_customer"),
        )
        df = df.merge(
            product_df, on="product_id", how="left", validate="many_to_one",
            suffixes=("", "_product"),
        )

        for col in DWD_ORDER_COLUMNS:
            if col not in df.columns:
                df[col] = pd.NA
        df = df[DWD_ORDER_COLUMNS]
        self.save(df, output_file)
        logger.info(f"DWD 完成 {output_file} 行数={len(df)}")
        return df