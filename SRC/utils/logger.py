import logging
import os

from SRC.config import path
from SRC.config.settings import LOG_LEVEL

os.makedirs(path.LOG_DIR, exist_ok=True)

logging.basicConfig(
    filename=path.LOG_FILE,
    level=getattr(logging, LOG_LEVEL),
    encoding="utf-8",
    format="%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s",
    filemode="a",
)
logger = logging.getLogger("ecommerce_etl")