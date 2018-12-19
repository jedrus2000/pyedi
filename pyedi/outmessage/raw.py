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
        logger.debug('Start writing to "%(out)s".', {'out': self._outstream})
        self._outstream = self._edi_storage.opendata_bin(filename=self.ta_info["filename"], mode="wb")
        self._outstream.write(self.root)
        self._outstream.close()
        logger.debug('End writing to "%(out)s".', {'out': self._outstream})
        self.ta_info["envelope"] = "raw"
        self.ta_info["merge"] = False
