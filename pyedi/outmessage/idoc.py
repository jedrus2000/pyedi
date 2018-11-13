try:
    from xml.etree import cElementTree as ET
except ImportError:
    from xml.etree import ElementTree as ET

try:
    import elementtree.ElementInclude as ETI
except ImportError:
    from xml.etree import ElementInclude as ETI

from pyedi.botslib.consts import *
from .fixed import Fixed

class Idoc(Fixed):
    def __init__(self, ta_info):
        super(Idoc, self).__init__(ta_info)
        self.recordnumber = (
            0
        )  # segment counter. For sequential recordnumbering in records.

    def _canonicaltree(self, node_instance, structure):
        self.headerrecordnumber = self.recordnumber
        super(idoc, self)._canonicaltree(node_instance, structure)

    def _canonicalfields(self, node_instance, record_definition):
        if self.ta_info["automaticcount"]:
            node_instance.record.update(
                {
                    "MANDT": self.ta_info["MANDT"],
                    "DOCNUM": self.ta_info["DOCNUM"],
                    "SEGNUM": str(self.recordnumber),
                    "PSGNUM": str(self.headerrecordnumber),
                    "HLEVEL": str(len(record_definition[MPATH])),
                }
            )
        else:
            node_instance.record.update(
                {"MANDT": self.ta_info["MANDT"], "DOCNUM": self.ta_info["DOCNUM"]}
            )
        super(Idoc, self)._canonicalfields(node_instance, record_definition)
        self.recordnumber += (
            1
        )  # tricky. EDI_DC is not counted, so I count after writing.
