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
from .grammar import Grammar


class Test(Grammar):
    """ For unit tests """

    defaultsyntax = {
        "has_structure": True,  # is True, read structure, recorddef, check these
        "checkcollision": True,
        "noBOTSID": False,
    }