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


class Edifact(Grammar):
    defaultsyntax = {
        "add_crlfafterrecord_sep": "\r\n",
        "charset": "UNOA",
        "checkcharsetin": "strict",  # strict, ignore or botsreplace (replace with char as set in bots.ini).
        "checkcharsetout": "strict",  # strict, ignore or botsreplace (replace with char as set in bots.ini).
        "contenttype": "application/EDIFACT",
        "decimaal": ".",
        "envelope": "edifact",
        "escape": "?",
        "field_sep": "+",
        "forceUNA": False,
        "merge": True,
        "record_sep": "'",
        "reserve": "*",
        "sfield_sep": ":",
        "skip_char": "\r\n",
        "version": "3",
        "UNB.S001.0080": "",
        "UNB.S001.0133": "",
        "UNB.S002.0007": "14",
        "UNB.S002.0008": "",
        "UNB.S002.0042": "",
        "UNB.S003.0007": "14",
        "UNB.S003.0014": "",
        "UNB.S003.0046": "",
        "UNB.S005.0022": "",
        "UNB.S005.0025": "",
        "UNB.0026": "",
        "UNB.0029": "",
        "UNB.0031": "",
        "UNB.0032": "",
        "UNB.0035": "0",
        # settings needed as defaults, but not useful for this editype
        "checkunknownentities": True,
        "forcequote": 0,  # csv only
        "quote_char": "",
        "record_tag_sep": "",  # Tradacoms/GTDI
        "triad": "",
        # bots internal, never change/overwrite
        "has_structure": True,  # is True, read structure, recorddef, check these
        "checkcollision": True,
        "lengthnumericbare": True,
        "stripfield_sep": True,
    }
    formatconvert = {"A": "A", "AN": "A", "N": "R"}