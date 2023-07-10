from pathlib import Path

from loguru import logger as _logger


def init_logger():
    log_path = Path("logs")
    log_path.mkdir(parents=True, exist_ok=True)
    _logger.add("logs/log-file.log", rotation="00:00",
                format="{time:YYYY-MM-DD at HH:mm:ss} | {name}:{module}:{function}:{line} | {level} | {message}")
    return _logger


logger = init_logger()
