"""生成电商练习数据，同时产出一份注入质量问题的脏数据副本。

输出（位于 --output-dir，默认 data）：
  raw/order.csv, raw/order_detail.csv, raw/customer.csv, raw/product.csv
  dirty/order.csv, dirty/order_detail.csv, dirty/customer.csv, dirty/product.csv
  dirty/quality_injection_manifest.csv

raw 数据业务一致，可直接用于 ETL；dirty 数据在 raw 基础上注入少量已知异常，
用于数据质量检查与治理练习。
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

PROVINCES = [
    ("110000", "北京市"), ("120000", "天津市"), ("130000", "河北省"),
    ("140000", "山西省"), ("150000", "内蒙古自治区"), ("210000", "辽宁省"),
    ("220000", "吉林省"), ("230000", "黑龙江省"), ("310000", "上海市"),
    ("320000", "江苏省"), ("330000", "浙江省"), ("340000", "安徽省"),
    ("350000", "福建省"), ("360000", "江西省"), ("370000", "山东省"),
    ("410000", "河南省"), ("420000", "湖北省"), ("430000", "湖南省"),
    ("440000", "广东省"), ("450000", "广西壮族自治区"), ("460000", "海南省"),
    ("500000", "重庆市"), ("510000", "四川省"), ("520000", "贵州省"),
    ("530000", "云南省"), ("540000", "西藏自治区"), ("610000", "陕西省"),
    ("620000", "甘肃省"), ("630000", "青海省"), ("640000", "宁夏回族自治区"),
    ("650000", "新疆维吾尔自治区"),
]

CATEGORIES = [
    ("CAT001", "手机数码"), ("CAT002", "电脑办公"), ("CAT003", "家用电器"),
    ("CAT004", "服装鞋包"), ("CAT005", "食品饮料"), ("CAT006", "美妆个护"),
    ("CAT007", "家居家装"), ("CAT008", "母婴用品"), ("CAT009", "运动户外"),
    ("CAT010", "图书文娱"), ("CAT011", "汽车用品"), ("CAT012", "医药保健"),
]

VALID_ORDER_STATUS = ["待支付", "已支付", "已发货", "已完成", "已取消", "已退款"]
VALID_SALE_STATUS = ["已支付", "已发货", "已完成"]


@dataclass(frozen=True)
class GeneratorConfig:
    orders: int = 100_000
    customers: int = 10_000
    products: int = 3_000
    shops: int = 500
    seed: int = 20260720
    start_date: str = "2025-01-01"
    end_date: str = "2025-12-31"
    dirty_rate: float = 0.001


def make_sequential_ids(prefix: str, count: int, width: int) -> np.ndarray:
    return np.array([f"{prefix}{i:0{width}d}" for i in range(1, count + 1)])


def make_random_datetimes(
    rng: np.random.Generator, start: str, end: str, size: int
) -> pd.DatetimeIndex:
    start_sec = pd.Timestamp(start).value // 10**9
    end_sec = pd.Timestamp(end).value // 10**9
    seconds = rng.integers(start_sec, end_sec + 1, size=size)
    return pd.to_datetime(seconds, unit="s")


def build_customers(cfg: GeneratorConfig, rng: np.random.Generator) -> pd.DataFrame:
    ids = make_sequential_ids("C", cfg.customers, 6)
    province_idx = rng.integers(0, len(PROVINCES), size=cfg.customers)
    register_time = make_random_datetimes(
        rng, "2022-01-01", "2024-12-31 23:59:59", cfg.customers
    )
    updated_at = register_time + pd.to_timedelta(
        rng.integers(0, 366, size=cfg.customers), unit="D"
    )
    return pd.DataFrame({
        "customer_id": ids,
        "customer_name": [f"客户{i:06d}" for i in range(1, cfg.customers + 1)],
        "gender": rng.choice(["男", "女", "未知"], size=cfg.customers, p=[0.49, 0.49, 0.02]),
        "age": rng.integers(18, 71, size=cfg.customers),
        "phone": [f"1{i:010d}" for i in range(1, cfg.customers + 1)],
        "email": [f"customer{i:06d}@example.com" for i in range(1, cfg.customers + 1)],
        "register_time": register_time,
        "member_level": rng.choice(
            ["普通", "银卡", "金卡", "钻石"], size=cfg.customers, p=[0.70, 0.18, 0.09, 0.03]
        ),
        "province_code": [PROVINCES[i][0] for i in province_idx],
        "province_name": [PROVINCES[i][1] for i in province_idx],
        "customer_status": rng.choice(["正常", "冻结"], size=cfg.customers, p=[0.99, 0.01]),
        "updated_at": updated_at,
    })


def build_products(cfg: GeneratorConfig, rng: np.random.Generator) -> pd.DataFrame:
    ids = make_sequential_ids("P", cfg.products, 6)
    category_idx = rng.integers(0, len(CATEGORIES), size=cfg.products)
    unit_price = np.round(rng.uniform(10, 10_000, size=cfg.products), 2)
    cost_price = np.round(unit_price * rng.uniform(0.50, 0.85, size=cfg.products), 2)
    created_at = make_random_datetimes(
        rng, "2022-01-01", "2024-12-31 23:59:59", cfg.products
    )
    updated_at = created_at + pd.to_timedelta(
        rng.integers(0, 366, size=cfg.products), unit="D"
    )
    return pd.DataFrame({
        "product_id": ids,
        "product_name": [f"商品{i:06d}" for i in range(1, cfg.products + 1)],
        "category_id": [CATEGORIES[i][0] for i in category_idx],
        "category_name": [CATEGORIES[i][1] for i in category_idx],
        "brand_name": [f"品牌{i:03d}" for i in rng.integers(1, 201, size=cfg.products)],
        "unit_price": unit_price,
        "cost_price": cost_price,
        "product_status": rng.choice(["在售", "下架"], size=cfg.products, p=[0.97, 0.03]),
        "created_at": created_at,
        "updated_at": updated_at,
    })


def build_orders_and_details(
    cfg: GeneratorConfig,
    rng: np.random.Generator,
    customers: pd.DataFrame,
    products: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    order_ids = make_sequential_ids("O", cfg.orders, 8)
    customer_ids = rng.choice(customers["customer_id"].to_numpy(), size=cfg.orders)
    order_time = make_random_datetimes(rng, cfg.start_date, cfg.end_date, cfg.orders)
    details_per_order = rng.integers(1, 6, size=cfg.orders)
    detail_count = int(details_per_order.sum())

    detail_order_ids = np.repeat(order_ids, details_per_order)
    detail_order_times = pd.DatetimeIndex(np.repeat(order_time.to_numpy(), details_per_order))
    product_idx = rng.integers(0, cfg.products, size=detail_count)
    product_ids = products["product_id"].to_numpy()[product_idx]
    unit_prices = products["unit_price"].to_numpy()[product_idx]
    quantities = rng.integers(1, 6, size=detail_count)
    gross_amount = np.round(unit_prices * quantities, 2)
    selected_discount = rng.choice(
        np.array([0.0, 5.0, 10.0, 20.0, 50.0]),
        size=detail_count,
        p=[0.55, 0.12, 0.13, 0.12, 0.08],
    )
    discount_amount = np.round(np.minimum(selected_discount, gross_amount * 0.30), 2)
    actual_amount = np.round(gross_amount - discount_amount, 2)
    detail_created_at = detail_order_times + pd.to_timedelta(
        rng.integers(0, 3_601, size=detail_count), unit="s"
    )

    details = pd.DataFrame({
        "order_detail_id": make_sequential_ids("OD", detail_count, 9),
        "order_id": detail_order_ids,
        "product_id": product_ids,
        "quantity": quantities,
        "unit_price": unit_prices,
        "discount_amount": discount_amount,
        "actual_amount": actual_amount,
        "created_at": detail_created_at,
    })

    order_amount = (
        details.groupby("order_id", sort=False)["actual_amount"]
        .sum()
        .reindex(order_ids)
        .to_numpy()
    )
    coupon_candidate = rng.choice(
        np.array([0.0, 10.0, 20.0, 50.0, 100.0, 200.0]),
        size=cfg.orders,
        p=[0.50, 0.12, 0.12, 0.12, 0.09, 0.05],
    )
    coupon_amount = np.round(np.minimum(coupon_candidate, order_amount * 0.20), 2)
    freight_amount = rng.choice(
        np.array([0.0, 6.0, 8.0, 12.0]), size=cfg.orders, p=[0.55, 0.15, 0.20, 0.10]
    )
    payable_amount = np.round(order_amount - coupon_amount + freight_amount, 2)
    province_idx = rng.integers(0, len(PROVINCES), size=cfg.orders)
    updated_at = order_time + pd.to_timedelta(
        rng.integers(0, 31, size=cfg.orders), unit="D"
    )

    orders = pd.DataFrame({
        "order_id": order_ids,
        "order_no": [
            f"NO{ts:%Y%m%d}{n:08d}" for n, ts in enumerate(order_time, 1)
        ],
        "customer_id": customer_ids,
        "shop_id": [
            f"S{n:05d}" for n in rng.integers(1, cfg.shops + 1, size=cfg.orders)
        ],
        "order_time": order_time,
        "order_status": rng.choice(
            VALID_ORDER_STATUS,
            size=cfg.orders,
            p=[0.03, 0.12, 0.18, 0.55, 0.08, 0.04],
        ),
        "order_amount": np.round(order_amount, 2),
        "coupon_amount": coupon_amount,
        "freight_amount": freight_amount,
        "payable_amount": payable_amount,
        "order_channel": rng.choice(["APP", "小程序", "PC", "线下"], size=cfg.orders),
        "receiver_province_code": [PROVINCES[i][0] for i in province_idx],
        "receiver_province_name": [PROVINCES[i][1] for i in province_idx],
        "updated_at": updated_at,
    })

    return orders, details


def sample_indices(rng: np.random.Generator, size: int, rate: float) -> np.ndarray:
    count = max(1, int(round(size * rate)))
    return rng.choice(size, size=min(count, size), replace=False)


def inject_dirty_data(
    cfg: GeneratorConfig,
    rng: np.random.Generator,
    customers: pd.DataFrame,
    products: pd.DataFrame,
    orders: pd.DataFrame,
    details: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    dirty_customers = customers.copy(deep=True)
    dirty_products = products.copy(deep=True)
    dirty_orders = orders.copy(deep=True)
    dirty_details = details.copy(deep=True)
    manifest: list[dict[str, object]] = []

    def record(dataset, row_id, rule, field, value, note):
        manifest.append({
            "dataset": dataset,
            "row_id": row_id,
            "rule_code": rule,
            "field": field,
            "injected_value": value,
            "description": note,
        })

    idx = sample_indices(rng, len(dirty_details), cfg.dirty_rate)
    split = len(idx) // 2
    dirty_details.loc[idx[:split], "quantity"] = -1
    dirty_details.loc[idx[split:], "quantity"] = 999
    for i in idx:
        row = dirty_details.loc[i]
        record("order_detail", row["order_detail_id"], "QUANTITY_RANGE", "quantity", row["quantity"], "商品数量超出1至5")

    idx = sample_indices(rng, len(dirty_details), cfg.dirty_rate)
    dirty_details.loc[idx, "actual_amount"] = np.round(
        dirty_details.loc[idx, "actual_amount"] * 1.20 + 1, 2
    )
    for i in idx:
        row = dirty_details.loc[i]
        record("order_detail", row["order_detail_id"], "DETAIL_AMOUNT_FORMULA", "actual_amount", row["actual_amount"], "明细金额不等于数量乘单价减优惠")

    idx = sample_indices(rng, len(dirty_details), cfg.dirty_rate)
    dirty_details.loc[idx, "product_id"] = [
        f"P_MISSING_{n:06d}" for n in range(1, len(idx) + 1)
    ]
    for i in idx:
        row = dirty_details.loc[i]
        record("order_detail", row["order_detail_id"], "PRODUCT_FK", "product_id", row["product_id"], "商品主数据不存在")

    idx = sample_indices(rng, len(dirty_details), cfg.dirty_rate)
    order_time_lookup = orders.set_index("order_id")["order_time"]
    dirty_details.loc[idx, "created_at"] = (
        dirty_details.loc[idx, "order_id"].map(order_time_lookup)
        - pd.to_timedelta(rng.integers(1, 31, size=len(idx)), unit="D")
    )
    for i in idx:
        row = dirty_details.loc[i]
        record("order_detail", row["order_detail_id"], "DETAIL_TIME", "created_at", row["created_at"], "明细时间早于订单时间")

    idx = sample_indices(rng, len(dirty_orders), cfg.dirty_rate)
    dirty_orders.loc[idx, "customer_id"] = [
        f"C_MISSING_{n:06d}" for n in range(1, len(idx) + 1)
    ]
    for i in idx:
        row = dirty_orders.loc[i]
        record("order", row["order_id"], "CUSTOMER_FK", "customer_id", row["customer_id"], "客户主数据不存在")

    idx = sample_indices(rng, len(dirty_orders), cfg.dirty_rate)
    thirds = np.array_split(idx, 3)
    dirty_orders.loc[thirds[0], "payable_amount"] = 0.0
    dirty_orders.loc[thirds[1], "payable_amount"] = -1.0
    dirty_orders.loc[thirds[2], "payable_amount"] = np.round(
        dirty_orders.loc[thirds[2], "payable_amount"] + 123.45, 2
    )
    for i in idx:
        row = dirty_orders.loc[i]
        record("order", row["order_id"], "ORDER_AMOUNT_FORMULA", "payable_amount", row["payable_amount"], "应付金额公式异常")

    idx = sample_indices(rng, len(dirty_orders), cfg.dirty_rate)
    dirty_orders.loc[idx, "order_status"] = "未知状态"
    for i in idx:
        row = dirty_orders.loc[i]
        record("order", row["order_id"], "ORDER_STATUS_ENUM", "order_status", row["order_status"], "订单状态不在标准枚举中")

    idx = sample_indices(rng, len(dirty_customers), cfg.dirty_rate)
    dirty_customers.loc[idx, "customer_name"] = pd.NA
    for i in idx:
        row = dirty_customers.loc[i]
        record("customer", row["customer_id"], "CUSTOMER_NAME_NULL", "customer_name", None, "客户名称为空")

    idx = sample_indices(rng, len(dirty_products), cfg.dirty_rate)
    dirty_products.loc[idx, "category_name"] = pd.NA
    for i in idx:
        row = dirty_products.loc[i]
        record("product", row["product_id"], "CATEGORY_NULL", "category_name", None, "商品分类为空")

    order_idx = sample_indices(rng, len(dirty_orders), cfg.dirty_rate / 2)
    dup_orders = dirty_orders.loc[order_idx].copy()
    dirty_orders = pd.concat([dirty_orders, dup_orders], ignore_index=True)
    for _, row in dup_orders.iterrows():
        record("order", row["order_id"], "DUPLICATE_ROW", "all", "duplicate", "订单整行重复")

    detail_idx = sample_indices(rng, len(dirty_details), cfg.dirty_rate / 2)
    dup_details = dirty_details.loc[detail_idx].copy()
    dirty_details = pd.concat([dirty_details, dup_details], ignore_index=True)
    for _, row in dup_details.iterrows():
        record("order_detail", row["order_detail_id"], "DUPLICATE_ROW", "all", "duplicate", "订单明细整行重复")

    return dirty_customers, dirty_products, dirty_orders, dirty_details, pd.DataFrame(manifest)


def validate_clean_data(customers, products, orders, details) -> None:
    errors: list[str] = []
    for name, frame, key in [
        ("customer", customers, "customer_id"),
        ("product", products, "product_id"),
        ("order", orders, "order_id"),
        ("order_detail", details, "order_detail_id"),
    ]:
        if frame[key].isna().any() or frame[key].duplicated().any():
            errors.append(f"{name}.{key} is null or duplicated")

    if not orders["customer_id"].isin(customers["customer_id"]).all():
        errors.append("order contains unknown customer_id")
    if not details["order_id"].isin(orders["order_id"]).all():
        errors.append("order_detail contains unknown order_id")
    if not details["product_id"].isin(products["product_id"]).all():
        errors.append("order_detail contains unknown product_id")
    if not details["quantity"].between(1, 5).all():
        errors.append("clean quantity is outside 1..5")

    expected_detail_amount = np.round(
        details["quantity"] * details["unit_price"] - details["discount_amount"], 2
    )
    if not np.allclose(details["actual_amount"], expected_detail_amount, atol=0.01):
        errors.append("actual_amount formula mismatch")

    detail_sum = details.groupby("order_id")["actual_amount"].sum()
    order_amount = orders.set_index("order_id")["order_amount"]
    if not np.allclose(order_amount.sort_index(), detail_sum.sort_index(), atol=0.01):
        errors.append("order_amount does not equal detail actual_amount sum")

    expected_payable = np.round(
        orders["order_amount"] - orders["coupon_amount"] + orders["freight_amount"], 2
    )
    if not np.allclose(orders["payable_amount"], expected_payable, atol=0.01):
        errors.append("payable_amount formula mismatch")

    order_time_lookup = orders.set_index("order_id")["order_time"]
    detail_order_time = details["order_id"].map(order_time_lookup)
    if (details["created_at"] < detail_order_time).any():
        errors.append("detail created_at is before order_time")

    if errors:
        raise ValueError("Clean data validation failed: " + "; ".join(errors))


def write_dataset(directory: Path, frames: dict[str, pd.DataFrame]) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    for filename, frame in frames.items():
        frame.to_csv(directory / filename, index=False, encoding="utf-8-sig")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="生成电商练习数据")
    parser.add_argument("--orders", type=int, default=100_000)
    parser.add_argument("--customers", type=int, default=10_000)
    parser.add_argument("--products", type=int, default=3_000)
    parser.add_argument("--shops", type=int, default=500)
    parser.add_argument("--seed", type=int, default=20260720)
    parser.add_argument("--dirty-rate", type=float, default=0.001)
    parser.add_argument("--output-dir", type=Path, default=Path("data"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.orders < 1 or args.customers < 1 or args.products < 1 or args.shops < 1:
        raise ValueError("orders/customers/products/shops 必须为正整数")
    if not 0 < args.dirty_rate <= 0.05:
        raise ValueError("dirty-rate 必须大于 0 且不超过 0.05")

    cfg = GeneratorConfig(
        orders=args.orders,
        customers=args.customers,
        products=args.products,
        shops=args.shops,
        seed=args.seed,
        dirty_rate=args.dirty_rate,
    )
    rng = np.random.default_rng(cfg.seed)

    customers = build_customers(cfg, rng)
    products = build_products(cfg, rng)
    orders, details = build_orders_and_details(cfg, rng, customers, products)
    validate_clean_data(customers, products, orders, details)

    dirty_customers, dirty_products, dirty_orders, dirty_details, manifest = inject_dirty_data(
        cfg, rng, customers, products, orders, details
    )

    clean_frames = {
        "customer.csv": customers,
        "product.csv": products,
        "order.csv": orders,
        "order_detail.csv": details,
    }
    dirty_frames = {
        "customer.csv": dirty_customers,
        "product.csv": dirty_products,
        "order.csv": dirty_orders,
        "order_detail.csv": dirty_details,
        "quality_injection_manifest.csv": manifest,
    }
    write_dataset(args.output_dir / "raw", clean_frames)
    write_dataset(args.output_dir / "dirty", dirty_frames)

    print("电商数据生成完成")
    print(f"干净数据: {(args.output_dir / 'raw').resolve()}")
    print(f"脏数据  : {(args.output_dir / 'dirty').resolve()}")
    print(f"客户数  : {len(customers):,}")
    print(f"商品数  : {len(products):,}")
    print(f"订单数  : {len(orders):,}")
    print(f"明细数  : {len(details):,}")
    print(f"注入问题: {len(manifest):,}")


if __name__ == "__main__":
    main()