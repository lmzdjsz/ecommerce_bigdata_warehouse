ORDER_RAW_SCHEMA = {
    "order_id": str, "order_no": str, "customer_id": str, "shop_id": str,
    "order_time": str, "order_status": str, "order_amount": str,
    "coupon_amount": str, "freight_amount": str, "payable_amount": str,
    "order_channel": str, "receiver_province_code": str,
    "receiver_province_name": str, "updated_at": str,
}

ORDER_DETAIL_RAW_SCHEMA = {
    "order_detail_id": str, "order_id": str, "product_id": str,
    "quantity": str, "unit_price": str, "discount_amount": str,
    "actual_amount": str, "created_at": str,
}

CUSTOMER_RAW_SCHEMA = {
    "customer_id": str, "customer_name": str, "gender": str, "age": str,
    "phone": str, "email": str, "register_time": str, "member_level": str,
    "province_code": str, "province_name": str, "customer_status": str,
    "updated_at": str,
}

PRODUCT_RAW_SCHEMA = {
    "product_id": str, "product_name": str, "category_id": str,
    "category_name": str, "brand_name": str, "unit_price": str,
    "cost_price": str, "product_status": str, "created_at": str,
    "updated_at": str,
}

DWD_ORDER_COLUMNS = [
    "order_id", "order_no", "customer_id", "shop_id", "order_time",
    "order_status", "order_channel", "order_amount", "coupon_amount",
    "freight_amount", "payable_amount", "receiver_province_code",
    "receiver_province_name", "customer_name", "member_level",
    "order_detail_id", "product_id", "quantity", "unit_price",
    "discount_amount", "actual_amount", "created_at",
    "product_name", "category_name",
]