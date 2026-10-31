import pandas as pd

from SRC.warehouse.base_builder import BaseBuilder
from SRC.config.settings import VALID_SALES_STATUSES
from SRC.utils.logger import logger


class DWSBuilder(BaseBuilder):
    def build_user_sales(self, dwd_file, output_file):
        logger.info("构建 DWS 用户销售主题")
        df = self.read(dwd_file)
        df["order_time"] = pd.to_datetime(df["order_time"], errors="coerce")
        df = df[df["order_status"].isin(VALID_SALES_STATUSES)].copy()

        order_level = df.drop_duplicates(subset=["order_id"]).copy()
        order_level["customer_name"] = order_level["customer_name"].fillna("未知客户")

        source_order_count = order_level["order_id"].nunique()
        source_total_amount = round(order_level["payable_amount"].sum(), 2)

        user_sales = order_level.groupby(
            ["customer_id", "customer_name"], dropna=False
        ).agg(
            order_count=("order_id", "nunique"),
            total_amount=("payable_amount", "sum"),
            first_order_time=("order_time", "min"),
            last_order_time=("order_time", "max"),
        ).reset_index()
        user_sales["avg_amount"] = (
            user_sales["total_amount"] / user_sales["order_count"]
        ).round(2)
        user_sales["total_amount"] = user_sales["total_amount"].round(2)

        dws_order_count = user_sales["order_count"].sum()
        dws_total_amount = round(user_sales["total_amount"].sum(), 2)
        if source_order_count != dws_order_count:
            raise ValueError(f"用户主题订单数核对失败: {source_order_count} != {dws_order_count}")
        if abs(source_total_amount - dws_total_amount) > 0.01:
            raise ValueError(f"用户主题金额核对失败: {source_total_amount} != {dws_total_amount}")

        self.save(user_sales, output_file)
        logger.info(f"DWS 用户主题完成 {output_file} 行数={len(user_sales)}")
        return user_sales

    def build_product_sales(self, dwd_file, output_file):
        logger.info("构建 DWS 商品销售主题")
        df = self.read(dwd_file)
        df = df[df["order_status"].isin(VALID_SALES_STATUSES)].copy()

        df["product_name"] = df["product_name"].fillna("未知商品")
        df["category_name"] = df["category_name"].fillna("未知分类")
        df["product_id"] = df["product_id"].fillna("UNKNOWN_PRODUCT")

        source_sales_count = int(df["quantity"].sum())
        source_sales_amount = round(df["actual_amount"].sum(), 2)

        product_sales = df.groupby(
            ["product_id", "product_name", "category_name"], dropna=False
        ).agg(
            sales_count=("quantity", "sum"),
            sales_amount=("actual_amount", "sum"),
        ).reset_index()
        product_sales["sales_amount"] = product_sales["sales_amount"].round(2)

        dws_sales_count = int(product_sales["sales_count"].sum())
        dws_sales_amount = round(product_sales["sales_amount"].sum(), 2)
        if source_sales_count != dws_sales_count:
            raise ValueError(f"商品主题销量核对失败: {source_sales_count} != {dws_sales_count}")
        if abs(source_sales_amount - dws_sales_amount) > 0.01:
            raise ValueError(f"商品主题金额核对失败: {source_sales_amount} != {dws_sales_amount}")

        self.save(product_sales, output_file)
        logger.info(f"DWS 商品主题完成 {output_file} 行数={len(product_sales)}")
        return product_sales