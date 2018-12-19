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


class Tradacoms(Grammar):
    defaultsyntax = {
        "add_crlfafterrecord_sep": "\r\n",
        "charset": "us-ascii",
        "checkcharsetin": "strict",  # strict, ignore or botsreplace (replace with char as set in bots.ini).
        "checkcharsetout": "strict",  # strict, ignore or botsreplace (replace with char as set in bots.ini).
        "contenttype": "application/text",
        "decimaal": ".",
        "envelope": "tradacoms",
        "escape": "?",
        "field_sep": "+",
        "merge": False,
        "record_sep": "'",
        "record_tag_sep": "=",  # Tradacoms/GTDI
        "sfield_sep": ":",
        "STX.STDS1": "ANA",
        "STX.STDS2": "1",
        "STX.FROM.02": "",
        "STX.UNTO.02": "",
        "STX.APRF": "",
        "STX.PRCD": "",
        # settings needed as defaults, but not useful for this editype
        "checkunknownentities": True,
        "forcequote": 0,  # csv only
        "indented": False,  # False:  output is one string (no cr/lf); True:  output is indented/human readable
        "quote_char": "",
        "reserve": "",
        "skip_char": "\r\n",
        "triad": "",
        # bots internal, never change/overwrite
        "has_structure": True,  # is True, read structure, recorddef, check these
        "checkcollision": True,
        "lengthnumericbare": True,
        "stripfield_sep": True,
    }
    formatconvert = {"X": "A", "9": "R", "9V9": "I"}