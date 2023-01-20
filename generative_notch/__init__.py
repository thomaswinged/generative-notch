import logging
from generative_notch.config import config


def init_logger(level: int = logging.DEBUG):
    import logging
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    logging.basicConfig(format=' %(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger()
    logger.setLevel(level)


def get_config(path: str = None):
    return config.get(path)
