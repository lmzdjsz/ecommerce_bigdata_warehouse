import numpy as np
import pandas as pd

from SRC.warehouse.base_builder import BaseBuilder
from SRC.config.settings import (
    VALID_SALES_STATUSES, VIP_AMOUNT, IMPORTANT_AMOUNT,
)
from SRC.utils.logger import logger


class ADSBuilder(BaseBuilder):
    def build_sales_summary(self, dwd_file, output_file):
        logger.info("构建 ADS 日销售指标")
        df = self.read(dwd_file)
        df = df[df["order_status"].isin(VALID_SALES_STATUSES)].copy()
        order_df = df.drop_duplicates(subset=["order_id"]).copy()
        order_df["order_time"] = pd.to_datetime(order_df["order_time"], errors="coerce")
        valid = order_df[order_df["order_time"].notna()].copy()
        valid["order_date"] = valid["order_time"].dt.strftime("%Y-%m-%d")

        sales = valid.groupby("order_date").agg(
            order_count=("order_id", "nunique"),
            user_count=("customer_id", "nunique"),
            sales_amount=("payable_amount", "sum"),
        ).reset_index()
        sales["avg_order_amount"] = (
            sales["sales_amount"] / sales["order_count"]
        ).round(2)
        sales["sales_amount"] = sales["sales_amount"].round(2)
        sales = sales.sort_values("order_date").reset_index(drop=True)

        self.save(sales, output_file)
        logger.info(f"ADS 日销售完成 {output_file} 行数={len(sales)}")
        return sales

    def build_user_summary(self, dws_user_file, output_file):
        logger.info("构建 ADS 用户运营指标")
        user = self.read(dws_user_file)

        def get_level(total):
            if total >= VIP_AMOUNT:
                return "VIP"
            if total >= IMPORTANT_AMOUNT:
                return "重点用户"
            return "普通用户"

        user["user_level"] = user["total_amount"].apply(get_level)
        self.save(user, output_file)
        logger.info(f"ADS 用户运营完成 {output_file} 行数={len(user)}")
        return user

    def build_user_rfm_base(self, dws_user_file, output_file):
        logger.info("构建 ADS RFM 基础")
        user = self.read(dws_user_file)
        user["last_order_time"] = pd.to_datetime(user["last_order_time"], errors="coerce")

        analysis_date = user["last_order_time"].max().normalize() + pd.Timedelta(days=1)
        rfm = user[["customer_id", "customer_name"]].copy()
        rfm["recency_days"] = (
            analysis_date - user["last_order_time"].dt.normalize()
        ).dt.days
        rfm["frequency"] = user["order_count"]
        rfm["monetary"] = user["total_amount"].round(2)
        rfm["analysis_date"] = analysis_date

        self.save(rfm, output_file)
        logger.info(f"ADS RFM 基础完成 {output_file} 行数={len(rfm)}")
        return rfm

    def build_user_rfm_segment(
        self, rfm_base_file, output_file, summary_file,
    ):
        logger.info("构建 ADS RFM 分群")
        rfm = self.read(rfm_base_file)

        def score(series, higher_is_better=True):
            pct = series.rank(method="average", pct=True, ascending=True)
            s = np.ceil(pct * 5).astype(int).clip(1, 5)
            return 6 - s if not higher_is_better else s

        rfm["r_score"] = score(rfm["recency_days"], higher_is_better=False)
        rfm["f_score"] = score(rfm["frequency"], higher_is_better=True)
        rfm["m_score"] = score(rfm["monetary"], higher_is_better=True)
        rfm["rfm_score"] = rfm["r_score"] + rfm["f_score"] + rfm["m_score"]
        rfm["rfm_code"] = (
            rfm["r_score"].astype(str)
            + rfm["f_score"].astype(str)
            + rfm["m_score"].astype(str)
        )

        segment_map = {
            (True, True, True): "重要价值用户",
            (True, False, True): "重要发展用户",
            (False, True, True): "重要保持用户",
            (False, False, True): "重要挽留用户",
            (True, True, False): "一般价值用户",
            (True, False, False): "一般发展用户",
            (False, True, False): "一般保持用户",
            (False, False, False): "一般挽留用户",
        }
        rfm["user_segment"] = [
            segment_map[(r >= 4, f >= 4, m >= 4)]
            for r, f, m in zip(rfm["r_score"], rfm["f_score"], rfm["m_score"])
        ]

        self.save(rfm, output_file)

        summary = rfm.groupby("user_segment").agg(
            user_count=("customer_id", "count"),
            avg_recency=("recency_days", "mean"),
            avg_frequency=("frequency", "mean"),
            total_monetary=("monetary", "sum"),
            avg_monetary=("monetary", "mean"),
        ).reset_index()
        summary["user_rate"] = (
            summary["user_count"] / summary["user_count"].sum() * 100
        ).round(2)
        summary["avg_recency"] = summary["avg_recency"].round(1)
        summary["avg_frequency"] = summary["avg_frequency"].round(1)
        summary["total_monetary"] = summary["total_monetary"].round(2)
        summary["avg_monetary"] = summary["avg_monetary"].round(2)
        self.save(summary, summary_file)
        logger.info(f"ADS RFM 分群完成 用户={len(rfm)} 群体={len(summary)}")
        return rfm, summary

    def build_product_summary(self, dws_product_file, output_file):
        logger.info("构建 ADS 商品运营指标")
        product = self.read(dws_product_file)
        product["sales_count_rank"] = product["sales_count"].rank(
            method="dense", ascending=False
        ).astype(int)
        product["sales_amount_rank"] = product["sales_amount"].rank(
            method="dense", ascending=False
        ).astype(int)
        product = product.sort_values(
            by=["sales_amount_rank", "sales_count_rank", "product_id"],
            ascending=[True, True, True],
        ).reset_index(drop=True)
        self.save(product, output_file)
        logger.info(f"ADS 商品运营完成 {output_file} 行数={len(product)}")
        return product