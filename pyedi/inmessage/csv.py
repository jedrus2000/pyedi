try:
    from xml.etree import cElementTree as ET
except ImportError:
    from xml.etree import ElementTree as ET

# bots-modules

from pyedi.botslib.consts import *

from .var import Var


class Csv(Var):
    """ class for ediobjects with Comma Separated Values"""

    def _lex(self):
        super(Csv, self)._lex()
        if self.ta_info["skip_firstline"]:
            # if it is an integer, skip that many lines
            # if True, skip just the first line
            if isinstance(self.ta_info["skip_firstline"], int):
                del self.lex_records[0 : self.ta_info["skip_firstline"]]
            else:
                del self.lex_records[0]
        if self.ta_info["noBOTSID"]:  # if read records contain no BOTSID: add it
            botsid = self.defmessage.structure[0][ID]  # add the recordname as BOTSID
            for lex_record in self.lex_records:
                lex_record[0:0] = [
                    {VALUE: botsid, POS: 0, LIN: lex_record[0][LIN], SFIELD: False}
                ]


