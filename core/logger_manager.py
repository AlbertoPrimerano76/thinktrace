import logging
from dotenv import load_dotenv
from datetime import datetime
from pathlib import Path
from rich.console import Console
from rich.logging import RichHandler
from .config_manager import config_manager, SCRIPT_DIR


class _LoggerManager:
    """🔹 Singleton Logger with Rich Formatting & Icons."""

    _instance = None
    _logger = None
    _initialized = False

    LOG_STYLES = {
        "DEBUG": "🐞",
        "INFO": "✅",
        "WARNING": "⚠️",
        "ERROR": "❌",
        "CRITICAL": "🔥",
    }

    def __new__(cls):
        load_dotenv()
        """Ensures Singleton Instance."""
        if cls._instance is None:
            cls._instance = super(_LoggerManager, cls).__new__(cls)
            cls._instance.console = Console()
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """🔹 Initialize logging settings."""
        if self._initialized:
            return

        log_level = config_manager.LOG_LEVEL
        enable_file_logging = config_manager.ENABLE_FILE_LOGGING
        log_folder = SCRIPT_DIR / config_manager.LOG_FOLDER
        logger_name = config_manager.APP_NAME 
        
        
        log_file_path = None
        if enable_file_logging:
            log_dir = Path(__file__).parent.parent / log_folder
            log_dir.mkdir(parents=True, exist_ok=True)
            log_file_path = log_dir / f"app_{datetime.now().strftime('%Y-%m-%d')}.log"

        handlers = [RichHandler(console=self.console, show_time=True, show_level=True, show_path=False)]

        if enable_file_logging and log_file_path:
            handlers.append(logging.FileHandler(log_file_path, mode="a", encoding="utf-8"))

        logging.basicConfig(
            level=getattr(logging, log_level, logging.INFO),
            handlers=handlers
        )

        for handler in handlers:
            handler.setFormatter(CustomFormatter())

        self._logger = logging.getLogger(logger_name)
        self._initialized = True

        self.info(f"✅ Logging initialized | Level: {log_level} | File Logging: {enable_file_logging}")
        if enable_file_logging and log_file_path:
            self.info(f"📂 Log file: {log_file_path}")

    @classmethod
    def get_logger(cls):
        """🔹 Return the logger instance."""
        if cls._instance is None:
            cls._instance = _LoggerManager()
        return cls._instance._logger

    @classmethod
    def debug(cls, msg):
        cls.get_logger().debug(msg)

    @classmethod
    def info(cls, msg):
        cls.get_logger().info(msg)

    @classmethod
    def warning(cls, msg):
        cls.get_logger().warning(msg)

    @classmethod
    def error(cls, msg):
        cls.get_logger().error(msg)

    @classmethod
    def critical(cls, msg):
        cls.get_logger().critical(msg)


class CustomFormatter(logging.Formatter):
    """🔹 Custom log format with icons using Rich."""

    def format(self, record):
        """Format log messages with icons and colors."""
        icon = _LoggerManager.LOG_STYLES.get(record.levelname, "🔵")
        record.msg = f"{icon} {record.msg}"
        return super().format(record)



logger = _LoggerManager().get_logger()