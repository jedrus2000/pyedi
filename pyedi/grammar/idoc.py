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
from .fixed import Fixed


class Idoc(Fixed):
    defaultsyntax = {
        "automaticcount": True,
        "charset": "us-ascii",
        "checkcharsetin": "strict",  # strict, ignore or botsreplace (replace with char as set in bots.ini).
        "checkcharsetout": "strict",  # strict, ignore or botsreplace (replace with char as set in bots.ini).
        "checkfixedrecordtoolong": False,
        "checkfixedrecordtooshort": False,
        "contenttype": "text/plain",
        "decimaal": ".",
        "envelope": "",
        "merge": False,
        "MANDT": "0",
        "DOCNUM": "0",
        # settings needed as defaults, but not useful for this editype
        "add_crlfafterrecord_sep": "",
        "checkunknownentities": True,
        "escape": "",
        "field_sep": "",
        "forcequote": 0,  # csv only
        "noBOTSID": False,  # allow fixed records without record ID.
        "quote_char": "",
        "record_sep": "\r\n",
        "record_tag_sep": "",  # Tradacoms/GTDI
        "reserve": "",
        "sfield_sep": "",
        "skip_char": "",
        "triad": "",
        # bots internal, never change/overwrite
        "has_structure": True,  # is True, read structure, recorddef, check these
        "checkcollision": True,
        "lengthnumericbare": False,
        "stripfield_sep": False,
    }