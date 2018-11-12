try:
    from xml.etree import cElementTree as ET
except ImportError:
    from xml.etree import ElementTree as ET

from gettext import gettext as _

# bots-modules

from pyedi.botslib import (
    logmap,
)

from .var import Var


class Tradacoms(Var):
    def checkenvelope(self):
        for nodestx in self.getloop({"BOTSID": "STX"}):
            logmap.debug("Start parsing tradacoms envelopes")
            endcount = nodestx.get({"BOTSID": "STX"}, {"BOTSID": "END", "NMST": None})
            messagecount = len(nodestx.children) - 1
            try:
                if int(endcount) != messagecount:
                    self.add2errorlist(
                        _(
                            "[E22]: Count in END is %(endcount)s; should be equal to number of messages %(messagecount)s.\n"
                        )
                        % {"endcount": endcount, "messagecount": messagecount}
                    )
            except:
                self.add2errorlist(
                    _('[E23]: Count of messages in END is invalid: "%(count)s".\n')
                    % {"count": endcount}
                )
            firstmessage = True
            for nodemhd in nodestx.getloop({"BOTSID": "STX"}, {"BOTSID": "MHD"}):
                if firstmessage:
                    nodestx.queries = {"messagetype": nodemhd.queries["messagetype"]}
                    firstmessage = False
                mtrcount = nodemhd.get(
                    {"BOTSID": "MHD"}, {"BOTSID": "MTR", "NOSG": None}
                )
                segmentcount = nodemhd.getcount()
                try:
                    if int(mtrcount) != segmentcount:
                        self.add2errorlist(
                            _(
                                "[E24]: Count in MTR is %(mtrcount)s; should be equal to number of segments %(segmentcount)s.\n"
                            )
                            % {"mtrcount": mtrcount, "segmentcount": segmentcount}
                        )
                except:
                    self.add2errorlist(
                        _('[E25]: Count of segments in MTR is invalid: "%(count)s".\n')
                        % {"count": mtrcount}
                    )
            logmap.debug("Parsing tradacoms envelopes is OK")

