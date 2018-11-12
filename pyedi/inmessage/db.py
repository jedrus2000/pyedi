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

