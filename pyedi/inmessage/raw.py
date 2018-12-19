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
    logger,
)

from .inmessage import InMessage


class Raw(InMessage):
    """ Input file is a raw bytestream.
        File is read, and passed to mapping script as inn.root
    """

    def initfromfile(self):
        logger.debug('Read edi file from: "%(in)s".', {'in': self.filehandler})
        # TODO - to delete
        """
        self.root = readdata_bin(filename=self.ta_info["filename"])
        """
        self.root = self.filehandler.read_data(name=self.ta_info["filename"])

    def nextmessage(self):
        yield self

