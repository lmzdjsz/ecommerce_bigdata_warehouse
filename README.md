# 电商数据仓库与经营分析项目

本项目参考 [245268037/ecommerce_project](https://github.com/245268037/ecommerce_project) 的设计与代码，重新独立实现一套电商离线数据仓库与经营分析系统。

## 项目目标

基于 Python、Pandas、PySpark、Linux Shell 构建电商离线数据仓库，从订单、订单明细、客户和商品四类原始数据出发，实现 ODS、DWD、DWS、ADS 分层加工，并完成数据质量检查、跨层指标核对、RFM 用户分群、商品 ABC 分析和 Linux 自动化运行。

## 技术栈

| 类别 | 技术 |
|------|------|
| 数据处理 | Python 3.13、Pandas、NumPy、PySpark 4.1.1、Spark SQL |
| 运行环境 | OpenJDK 17、Hadoop 3.1.3（伪分布式）、HDFS、YARN |
| 数据存储 | CSV、Parquet + Snappy、SQLite |
| 工程化 | Linux Bash、cron、flock、Git |
| 测试 | Pytest |

## 数据仓库架构

```text
                         ┌─ Pandas / NumPy
                         │      ↓
RAW 原始 CSV ── 数据质量检查 ─┤  ODS → DWD → DWS → ADS → BI 数据集
                         │
                         └─ PySpark / Spark SQL
                                ↓
                            ODS → DWD → DWS → ADS
                                ↓
                            Parquet + Snappy
                                ↓
                          跨层验收与性能体检
```

## 分层职责

| 层级 | 职责 |
|------|------|
| RAW | 保存订单、订单明细、客户和商品原始 CSV |
| ODS | 保留源数据并统一字段结构和技术字段 |
| DWD | 以订单明细为核心，关联订单、客户和商品信息 |
| DWS | 按用户、商品和地区形成主题汇总数据 |
| ADS | 生成每日销售、月度趋势、RFM 和商品 ABC 指标 |
| BI | 构建事实表、维度表和分析模型 |

## 项目结构

```text
ecommerce-bigdata-warehouse/
├── SRC/                     # 数据质量检查、清洗、ETL 主流程、数仓构建
│   ├── checker/             # 数据质量检查
│   ├── cleaner/             # 数据清洗
│   ├── config/              # 路径、字段和业务配置
│   ├── diagnostics/         # 数据问题诊断
│   ├── exporter/            # 质量报告导出
│   ├── pipeline/            # Pandas ETL 主流程
│   ├── utils/               # 日志、文件和任务工具
│   └── warehouse/           # Pandas 数仓构建程序
├── spark_learning/          # Spark 数仓分层与优化练习
├── sql_learning/            # SQL 颗粒度与聚合练习
├── scripts/                 # Shell 运维脚本
├── tests/                   # 单元测试
├── generate_ecommerce_data.py
├── requirements.txt
├── run_etl.sh               # Pandas ETL 流水线
├── run_spark_warehouse.sh   # Spark 数仓流水线
├── environment-check.txt    # 环境检查记录
└── README.md
```

## 运行方式

```bash
# 1. 创建虚拟环境
python3 -m venv .venv
source .venv/bin/activate

# 2. 安装依赖
python -m pip install -r requirements.txt

# 3. 生成练习数据
python generate_ecommerce_data.py

# 4. 执行 Pandas ETL
./run_etl.sh

# 5. 执行 Spark 数仓
./run_spark_warehouse.sh

# 6. 运行测试
PYTHONPATH="$PWD/SRC" python -m pytest tests -v
```

## 说明

- `reference/ecommerce_project/`（位于上级目录）为参考原仓库，本项目代码独立重写，不直接复制。
- 有效销售状态统一定义为：已支付、已发货、已完成。
- RFM 分析基准日：2025-12-31。