from datetime import datetime

from SRC.cleaner.data_cleaner import DataCleaner
from SRC.warehouse.ods_builder import ODSBuilder
from SRC.warehouse.dwd_builder import DWDBuilder
from SRC.warehouse.dws_builder import DWSBuilder
from SRC.warehouse.ads_builder import ADSBuilder
from SRC.config import path
from SRC.config.schema import (
    ORDER_RAW_SCHEMA, ORDER_DETAIL_RAW_SCHEMA,
    CUSTOMER_RAW_SCHEMA, PRODUCT_RAW_SCHEMA,
)
from SRC.utils.logger import logger
from SRC.utils.reader import save_csv
import pandas as pd


class ETLPipeline:
    def __init__(self):
        self.cleaner = DataCleaner()
        self.ods = ODSBuilder()
        self.dwd = DWDBuilder()
        self.dws = DWSBuilder()
        self.ads = ADSBuilder()

    def check_file(self):
        for f in [path.RAW_ORDER, path.RAW_ORDER_DETAIL, path.RAW_CUSTOMER, path.RAW_PRODUCT]:
            import os
            if not os.path.exists(f):
                raise FileNotFoundError(f"输入文件不存在: {f}")
        logger.info("输入文件检查通过")

    def clean(self):
        logger.info("=== 步骤 1: 数据清洗 ===")
        self.cleaner.clean(path.RAW_ORDER, path.CLEAN_ORDER, ORDER_RAW_SCHEMA)
        self.cleaner.clean(path.RAW_ORDER_DETAIL, path.CLEAN_ORDER_DETAIL, ORDER_DETAIL_RAW_SCHEMA)
        self.cleaner.clean(path.RAW_CUSTOMER, path.CLEAN_CUSTOMER, CUSTOMER_RAW_SCHEMA)
        self.cleaner.clean(path.RAW_PRODUCT, path.CLEAN_PRODUCT, PRODUCT_RAW_SCHEMA)

    def build_ods(self):
        logger.info("=== 步骤 2: 构建 ODS ===")
        self.ods.build_ods(path.CLEAN_ORDER, path.ODS_ORDER, ORDER_RAW_SCHEMA)
        self.ods.build_ods(path.CLEAN_ORDER_DETAIL, path.ODS_ORDER_DETAIL, ORDER_DETAIL_RAW_SCHEMA)
        self.ods.build_ods(path.CLEAN_CUSTOMER, path.ODS_CUSTOMER, CUSTOMER_RAW_SCHEMA)
        self.ods.build_ods(path.CLEAN_PRODUCT, path.ODS_PRODUCT, PRODUCT_RAW_SCHEMA)

    def build_dwd(self):
        logger.info("=== 步骤 3: 构建 DWD ===")
        return self.dwd.build_order_detail(
            path.ODS_ORDER, path.ODS_ORDER_DETAIL,
            path.ODS_CUSTOMER, path.ODS_PRODUCT, path.DWD_ORDER_DETAIL,
        )

    def build_dws(self):
        logger.info("=== 步骤 4: 构建 DWS ===")
        self.dws.build_user_sales(path.DWD_ORDER_DETAIL, path.DWS_USER_SALES)
        self.dws.build_product_sales(path.DWD_ORDER_DETAIL, path.DWS_PRODUCT_SALES)

    def build_ads(self):
        logger.info("=== 步骤 5: 构建 ADS ===")
        self.ads.build_sales_summary(path.DWD_ORDER_DETAIL, path.ADS_SALES_SUMMARY)
        self.ads.build_user_summary(path.DWS_USER_SALES, path.ADS_USER_SUMMARY)
        self.ads.build_user_rfm_base(path.DWS_USER_SALES, path.ADS_USER_RFM_BASE)
        self.ads.build_user_rfm_segment(
            path.ADS_USER_RFM_BASE,
            path.ADS_USER_RFM_SEGMENT,
            path.ADS_USER_RFM_SEGMENT_SUMMARY,
        )
        self.ads.build_product_summary(path.DWS_PRODUCT_SALES, path.ADS_PRODUCT_SUMMARY)

    def write_job_log(self, start, end, status):
        cost = (end - start).total_seconds()
        row = pd.DataFrame([{
            "job_name": "ecommerce_etl",
            "start_time": start.strftime("%Y-%m-%d %H:%M:%S"),
            "end_time": end.strftime("%Y-%m-%d %H:%M:%S"),
            "status": status,
            "cost_seconds": round(cost, 2),
        }])
        import os
        if os.path.exists(path.ETL_JOB_LOG):
            old = pd.read_csv(path.ETL_JOB_LOG, encoding="utf-8-sig")
            row = pd.concat([old, row], ignore_index=True)
        save_csv(row, path.ETL_JOB_LOG)

    def run(self):
        start = datetime.now()
        status = "SUCCESS"
        try:
            self.check_file()
            self.clean()
            self.build_ods()
            self.build_dwd()
            self.build_dws()
            self.build_ads()
            logger.info("ETL 全流程完成")
        except Exception as e:
            status = "FAILED"
            logger.error(f"ETL 失败: {e}")
            raise
        finally:
            end = datetime.now()
            self.write_job_log(start, end, status)