import logging


def get_default_logger_name():
    return __name__.split(".")[0]


default_logger_name = get_default_logger_name()

logging.getLogger(default_logger_name).addHandler(logging.NullHandler())
logger = logging.getLogger(default_logger_name)

logmap = logging.getLogger("mapping")  # logger for mapping in bots-engine


