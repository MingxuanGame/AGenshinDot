import logging
from typing import Dict
from pathlib import Path
from datetime import time, timedelta

import richuru
from loguru import logger

from .typing import LogLevel

LEVELS: Dict[LogLevel, int] = {
    "TRACE": 5,
    "DEBUG": 10,
    "INFO": 20,
    "SUCCESS": 25,
    "WARNING": 30,
    "ERROR": 40,
    "CRITICAL": 50,
}


def patch_logger(
    level: LogLevel,
    expire_time: timedelta = timedelta(weeks=2),
    patch_stdout: bool = True,
    enable_db_log: bool = False,
):
    logger.add(
        Path("log") / "{time:YYYY-MM-DD}" / "info.log",
        level=level,
        rotation=time(),
        retention=expire_time,
    )
    logger.add(
        Path("log") / "{time:YYYY-MM-DD}" / "error.log",
        level="ERROR",
        rotation=time(),
        retention=expire_time,
    )
    if patch_stdout:
        from sys import stdout

        logger.remove(0)
        logger.add(stdout, level=level)

    if enable_db_log:
        for log_name in ("sqlalchemy.engine.Engine",):
            logging_logger = logging.getLogger(log_name)
            logging_logger.setLevel(LEVELS.get(level, 20))
            logging_logger.handlers.clear()
            logging_logger.addHandler(richuru.LoguruHandler())
