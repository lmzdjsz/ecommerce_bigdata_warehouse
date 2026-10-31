from datetime import datetime

from SRC.warehouse.base_builder import BaseBuilder
from SRC.config.settings import SOURCE_SYSTEM
from SRC.utils.logger import logger


class ODSBuilder(BaseBuilder):
    def build_ods(self, input_file, output_file, schema):
        logger.info(f"构建 ODS {input_file}")
        df = self.read(input_file, schema)
        etl_time = datetime.now()
        df["etl_time"] = etl_time
        df["source_system"] = SOURCE_SYSTEM
        df["etl_batch"] = etl_time.strftime("%Y%m%d%H%M%S")
        self.save(df, output_file)
        logger.info(f"ODS 完成 {output_file} 行数={len(df)}")
        return df