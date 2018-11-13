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

