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
try:
    from xml.etree import cElementTree as ET
except ImportError:
    from xml.etree import ElementTree as ET

try:
    import elementtree.ElementInclude as ETI
except ImportError:
    from xml.etree import ElementInclude as ETI

from .var import Var


class X12(Var):
    def _getescapechars(self):
        terug = (
                self.ta_info["record_sep"]
                + self.ta_info["field_sep"]
                + self.ta_info["sfield_sep"]
        )
        if self.ta_info["version"] >= "00403":
            terug += self.ta_info["reserve"]
        return terug

