"""
Configures a centralized, structured, and colored logger for the application.
"""
import logging
import logging.handlers
import sys
from pathlib import Path

import colorlog

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "bot.log"

# 1. Create the main logger
logger = logging.getLogger("trading_bot")
logger.setLevel(logging.DEBUG)  # Set the lowest level to capture all messages

# 2. Create a handler for console output with coloring
console_handler = colorlog.StreamHandler(sys.stdout)
console_formatter = colorlog.ColoredFormatter(
    "%(log_color)s%(levelname)-8s%(reset)s %(blue)s%(name)-12s%(reset)s %(message)s",
    log_colors={
        "DEBUG": "cyan",
        "INFO": "green",
        "WARNING": "yellow",
        "ERROR": "red",
        "CRITICAL": "red,bg_white",
    },
)
console_handler.setFormatter(console_formatter)
console_handler.setLevel(logging.INFO)  # Only show INFO and above on console

# 3. Create a rotating file handler for logs on disk
# Rotates when the file reaches 40 MB, keeps 5 backup files.
file_handler = logging.handlers.RotatingFileHandler(
    LOG_FILE, maxBytes=40 * 1024 * 1024, backupCount=5
)
file_formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
file_handler.setFormatter(file_formatter)
file_handler.setLevel(logging.DEBUG)  # Log everything to the file

# 4. Add the handlers to the logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)

# Prevent logging from propagating to the root logger
logger.propagate = False

def get_logger(name: str) -> logging.Logger:
    """
    Returns a child logger with the given name.
    This allows for component-specific logging, e.g., get_logger(__name__).
    """
    return logging.getLogger(f"trading_bot.{name}")
