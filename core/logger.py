import logging
import sys

class FlushingStreamHandler(logging.StreamHandler):
    """Ensures log messages flush to stdout immediately on Windows and CI."""
    def emit(self, record):
        super().emit(record)
        self.flush()

def setup_logger(name: str = "C2C_Agent") -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-7s | %(message)s",
            datefmt="%H:%M:%S"
        )
        handler = FlushingStreamHandler(sys.stdout)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.propagate = False
    return logger

# Default singleton instance
logger = setup_logger()

# Backwards-compatibility alias for core/__init__.py
build_logger = setup_logger