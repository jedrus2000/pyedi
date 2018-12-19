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
from pyedi.botslib import (
    readdata_pickled,
    logger,
)

from .inmessage import InMessage


class Db(InMessage):
    """ For database connector: reading from database.
        Communication script delivers a file with a pickled object;
        File is read, object is unpickled, object is passed to the mapping script as inn.root.
    """

    def initfromfile(self):
        logger.debug('Read edi file "%(filename)s".', self.ta_info)
        self.root = readdata_pickled(filename=self.ta_info["filename"])

    def nextmessage(self):
        yield self

