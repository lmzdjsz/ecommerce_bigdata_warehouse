#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

PYTHON="${PYTHON:-python3}"
MAIN_FILE="SRC/main.py"
LOCK_FILE=".etl.lock"
LOG_DIR="logs"
RUN_TIME="$(date '+%Y%m%d_%H%M%S')"
RUN_LOG="$LOG_DIR/etl_run_${RUN_TIME}.log"

mkdir -p "$LOG_DIR"

exec 9>"$LOCK_FILE"
if ! flock -n 9; then
    echo "ETL 已在运行，退出" | tee -a "$RUN_LOG"
    exit 2
fi

echo "=== ETL 启动 ${RUN_TIME} ===" | tee -a "$RUN_LOG"

if [ ! -f "$MAIN_FILE" ]; then
    echo "主程序不存在: $MAIN_FILE" | tee -a "$RUN_LOG"
    exit 1
fi

for f in data/raw/order.csv data/raw/order_detail.csv data/raw/customer.csv data/raw/product.csv; do
    if [ ! -s "$f" ]; then
        echo "输入文件缺失或为空: $f" | tee -a "$RUN_LOG"
        exit 1
    fi
done
echo "输入文件检查通过" | tee -a "$RUN_LOG"

echo "=== 执行 Python ETL ===" | tee -a "$RUN_LOG"
PYTHONPATH="$SCRIPT_DIR" "$PYTHON" "$MAIN_FILE" 2>&1 | tee -a "$RUN_LOG"
PIPELINE_STATUS=${PIPESTATUS[0]}

if [ "$PIPELINE_STATUS" -ne 0 ]; then
    echo "ETL 失败，状态码=$PIPELINE_STATUS" | tee -a "$RUN_LOG"
    exit "$PIPELINE_STATUS"
fi

echo "=== 检查输出文件 ===" | tee -a "$RUN_LOG"
for f in \
    warehouse/dwd/dwd_order_detail.csv \
    warehouse/dws/dws_user_sales.csv \
    warehouse/dws/dws_product_sales.csv \
    warehouse/ads/ads_sales_summary.csv \
    warehouse/ads/ads_user_summary.csv \
    warehouse/ads/ads_product_summary.csv \
    warehouse/ads/ads_user_rfm_segment.csv \
    warehouse/ads/ads_user_rfm_segment_summary.csv; do
    if [ ! -s "$f" ]; then
        echo "输出文件缺失或为空: $f" | tee -a "$RUN_LOG"
        exit 1
    fi
    lines=$(wc -l < "$f")
    echo "  $f: ${lines} 行" | tee -a "$RUN_LOG"
done

echo "=== ETL 全流程成功 ===" | tee -a "$RUN_LOG"