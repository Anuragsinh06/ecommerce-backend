import logging
import sys
from pathlib import Path
from loguru import logger
import json

class InterceptHandler(logging.Handler):
    loglevel_mapping = {
        50: 'CRITICAL',
        40: 'ERROR',
        30: 'WARNING',
        20: 'INFO',
        10: 'DEBUG',
        0: 'NOTSET',
    }

    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except AttributeError:
            level = self.loglevel_mapping[record.levelno]

        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        log = logger.bind(request_id='app')
        log.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


class CustomizeLogger:

    @classmethod
    def make_logger(cls, config_path: str):
        config = cls.load_logging_config(config_path)
        
        # --- SAFETY LOGIC START ---
        # If config is None, or 'logger' key is missing, we create a default dict
        # This prevents the 'NoneType' AttributeError
        logging_config = config.get('logger') if config and isinstance(config, dict) else None

        if logging_config is None:
            print(f"--- WARNING: Logging config not found at {config_path} ---")
            print("--- Using default internal logging configuration ---")
            logging_config = {
                "path": "logs/main.log",
                "level": "INFO",
                "rotation": "500 MB",
                "retention": "10 days",
                "format": "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>"
            }
        # --- SAFETY LOGIC END ---

        logger_instance = cls.customize_logging(
            filepath=logging_config.get('path', 'logs/main.log'),
            level=logging_config.get('level', 'INFO'),
            retention=logging_config.get('retention', '10 days'),
            rotation=logging_config.get('rotation', '500 MB'),
            format=logging_config.get('format', "{time} {level} {message}")
        )
        return logger_instance

    @classmethod
    def customize_logging(cls, filepath: str, level: str, rotation: str, retention: str, format: str):
        logger.remove()
        
        # Console Log
        logger.add(sys.stdout, enqueue=True, backtrace=True, level=level.upper(), format=format)
        
        # File Log (Ensures the directory exists)
        log_file = Path(filepath)
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        logger.add(
            str(log_file),
            rotation=rotation,
            retention=retention,
            enqueue=True,
            backtrace=True,
            level=level.upper(),
            format=format
        )
        
        logging.basicConfig(handlers=[InterceptHandler()], level=0)
        logging.getLogger("uvicorn.access").handlers = [InterceptHandler()]
        for _log in ['uvicorn', 'uvicorn.error', 'fastapi']:
            _logger = logging.getLogger(_log)
            _logger.handlers = [InterceptHandler()]

        return logger.bind(request_id=None, method=None)

    @classmethod
    def load_logging_config(cls, config_path: str):
        try:
            with open(config_path, 'r') as config_file:
                return json.load(config_file)
        except Exception as e:
            # If file is missing or corrupted, return empty dict so app doesn't crash
            return {}