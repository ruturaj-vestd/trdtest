from loguru import logger


def configure_logging() -> None:
    logger.remove()
    logger.add(lambda msg: print(msg, end=""), level="INFO")
