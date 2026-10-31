import os

CURRENT_DIR = os.path.dirname(__file__)
BASE_DIR = os.path.dirname(os.path.dirname(CURRENT_DIR))
DATA_DIR = os.path.join(BASE_DIR, "data")
WAREHOUSE_DIR = os.path.join(BASE_DIR, "warehouse")
LOG_DIR = os.path.join(BASE_DIR, "logs")

RAW_DIR = os.path.join(DATA_DIR, "raw")
CLEAN_DIR = os.path.join(DATA_DIR, "clean")
REPORT_DIR = os.path.join(DATA_DIR, "report")
METADATA_DIR = os.path.join(DATA_DIR, "metadata")

ODS_DIR = os.path.join(WAREHOUSE_DIR, "ods")
DWD_DIR = os.path.join(WAREHOUSE_DIR, "dwd")
DWS_DIR = os.path.join(WAREHOUSE_DIR, "dws")
ADS_DIR = os.path.join(WAREHOUSE_DIR, "ads")

RAW_ORDER = os.path.join(RAW_DIR, "order.csv")
RAW_ORDER_DETAIL = os.path.join(RAW_DIR, "order_detail.csv")
RAW_CUSTOMER = os.path.join(RAW_DIR, "customer.csv")
RAW_PRODUCT = os.path.join(RAW_DIR, "product.csv")

CLEAN_ORDER = os.path.join(CLEAN_DIR, "cleaner_order.csv")
CLEAN_ORDER_DETAIL = os.path.join(CLEAN_DIR, "cleaner_order_detail.csv")
CLEAN_CUSTOMER = os.path.join(CLEAN_DIR, "cleaner_customer.csv")
CLEAN_PRODUCT = os.path.join(CLEAN_DIR, "cleaner_product.csv")

ODS_ORDER = os.path.join(ODS_DIR, "ods_order.csv")
ODS_ORDER_DETAIL = os.path.join(ODS_DIR, "ods_order_detail.csv")
ODS_CUSTOMER = os.path.join(ODS_DIR, "ods_customer.csv")
ODS_PRODUCT = os.path.join(ODS_DIR, "ods_product.csv")

DWD_ORDER_DETAIL = os.path.join(DWD_DIR, "dwd_order_detail.csv")

DWS_USER_SALES = os.path.join(DWS_DIR, "dws_user_sales.csv")
DWS_PRODUCT_SALES = os.path.join(DWS_DIR, "dws_product_sales.csv")

ADS_SALES_SUMMARY = os.path.join(ADS_DIR, "ads_sales_summary.csv")
ADS_USER_SUMMARY = os.path.join(ADS_DIR, "ads_user_summary.csv")
ADS_PRODUCT_SUMMARY = os.path.join(ADS_DIR, "ads_product_summary.csv")
ADS_USER_RFM_BASE = os.path.join(ADS_DIR, "ads_user_rfm_base.csv")
ADS_USER_RFM_SEGMENT = os.path.join(ADS_DIR, "ads_user_rfm_segment.csv")
ADS_USER_RFM_SEGMENT_SUMMARY = os.path.join(ADS_DIR, "ads_user_rfm_segment_summary.csv")

ETL_JOB_LOG = os.path.join(METADATA_DIR, "etl_job_log.csv")
LOG_FILE = os.path.join(LOG_DIR, "etl.log")

DIR_LIST = [
    RAW_DIR, CLEAN_DIR, REPORT_DIR, METADATA_DIR,
    ODS_DIR, DWD_DIR, DWS_DIR, ADS_DIR, LOG_DIR,
]
for d in DIR_LIST:
    os.makedirs(d, exist_ok=True)