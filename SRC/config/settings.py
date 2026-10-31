LOG_LEVEL = "INFO"
CSV_ENCODING = "utf-8-sig"
CSV_INDEX = False
TIME_FORMAT = "%Y-%m-%d %H:%M:%S"
SOURCE_SYSTEM = "ECommerce"
ETL_BATCH_SIZE = 10000
ENV = "dev"

DEFAULT_DTYPE = {
    "receiver_province_code": str,
    "customer_id": str,
    "product_id": str,
    "shop_id": str,
    "order_id": str,
    "order_detail_id": str,
    "province_code": str,
    "category_id": str,
}

TECH_COLUMNS = ["etl_time", "source_system", "etl_batch"]

VIP_AMOUNT = 10000
IMPORTANT_AMOUNT = 5000

VALID_SALES_STATUSES = ("已支付", "已发货", "已完成")