from SRC.pipeline.etl_pipeline import ETLPipeline
from SRC.utils.logger import logger


def main():
    logger.info("启动电商 ETL 项目")
    pipeline = ETLPipeline()
    pipeline.run()


if __name__ == "__main__":
    main()