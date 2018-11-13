from gettext import gettext as _

try:
    from xml.etree import cElementTree as ET
except ImportError:
    from xml.etree import ElementTree as ET

try:
    import elementtree.ElementInclude as ETI
except ImportError:
    from xml.etree import ElementInclude as ETI

from pyedi.botslib import (
    opendata_bin,
    OutMessageError,
    logger,
)

from .outmessage import OutMessage

class Raw(OutMessage):
    """ Mapping script delivers a raw bytestream in out.root.
        Bytestream is saved.
    """

    def __init__(self, ta_info):
        super(Raw, self).__init__(ta_info)
        self.root = (
            None
        )  # make root None; root is not a Node-object anyway; None can easy be tested when writing.

    def writeall(self):
        if self.root is None:
            raise OutMessageError(
                _("No outgoing message")
            )  # then there is nothing to write...
        logger.debug('Start writing to file "%(filename)s".', self.ta_info)
        self._outstream = opendata_bin(self.ta_info["filename"], "wb")
        self._outstream.write(self.root)
        self._outstream.close()
        logger.debug('End writing to file "%(filename)s".', self.ta_info)
        self.ta_info["envelope"] = "raw"
        self.ta_info["merge"] = False
