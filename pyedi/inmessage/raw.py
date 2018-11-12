from pyedi.botslib import (
    readdata_bin,
    logger,
)

from .inmessage import InMessage


class Raw(InMessage):
    """ Input file is a raw bytestream.
        File is read, and passed to mapping script as inn.root
    """

    def initfromfile(self):
        logger.debug('Read edi file "%(filename)s".', self.ta_info)
        self.root = readdata_bin(filename=self.ta_info["filename"])

    def nextmessage(self):
        yield self

