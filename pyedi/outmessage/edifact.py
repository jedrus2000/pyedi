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
from .var import Var


class Edifact(Var):
    def _getescapechars(self):
        terug = (
                self.ta_info["record_sep"]
                + self.ta_info["field_sep"]
                + self.ta_info["sfield_sep"]
                + self.ta_info["escape"]
        )
        if self.ta_info["version"] >= "4":
            terug += self.ta_info["reserve"]
        return terug
