import logging


def get_logger(name: str = "app") -> logging.Logger:
    """Return a configured logger."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        fmt = "%(asctime)s | %(name)s | %(levelname)s | %(message)s"
        handler.setFormatter(logging.Formatter(fmt))
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger

