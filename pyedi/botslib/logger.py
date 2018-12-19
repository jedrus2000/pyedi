"""
This is modified code of Bots project:
    http://bots.sourceforge.net/en/index.shtml
    ttp://bots.readthedocs.io
    https://github.com/eppye-bots/bots

originally created by Henk-Jan Ebbers.

This code include also changes from other forks, specially from:
    https://github.com/bots-edi

This project, as original Bots is licenced under GNU GENERAL PUBLIC LICENSE Version 3; for full
text: http://www.gnu.org/copyleft/gpl.html
"""
import logging


def get_default_logger_name():
    return __name__.split(".")[0]


default_logger_name = get_default_logger_name()

logging.getLogger(default_logger_name).addHandler(logging.NullHandler())
logger = logging.getLogger(default_logger_name)

logmap = logging.getLogger("mapping")  # logger for mapping in bots-engine


