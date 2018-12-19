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
)
from .var import Var


class Tradacoms(Var):
    def _getescapechars(self):
        terug = (
                self.ta_info["record_sep"]
                + self.ta_info["field_sep"]
                + self.ta_info["sfield_sep"]
                + self.ta_info["escape"]
                + self.ta_info["record_tag_sep"]
        )
        return terug

    def writeall(self):
        """ writeall is called for writing all 'real' outmessage objects; but not for enveloping.
            writeall is call from transform.translate()
        """
        self.nrmessagewritten = 0
        if not self.root.children:
            raise OutMessageError(
                _("No outgoing message")
            )  # then there is nothing to write...
        messagetype = self.ta_info["messagetype"]
        for tradacomsmessage in self.root.getloop({"BOTSID": "STX"}, {"BOTSID": "MHD"}):
            self.ta_info["messagetype"] = tradacomsmessage.get(
                {"BOTSID": "MHD", "TYPE.01": None}
            ) + tradacomsmessage.get({"BOTSID": "MHD", "TYPE.02": None})
            self.messagegrammarread(typeofgrammarfile="grammars")
            if not self.nrmessagewritten:
                self._initwrite()
            self.checkmessage(tradacomsmessage, self.defmessage)
            self.checkforerrorlist()
            self._write(tradacomsmessage)
            self.nrmessagewritten += 1
        self.ta_info["messagetype"] = messagetype
        self._closewrite()
        self.ta_info["nrmessages"] = self.nrmessagewritten
