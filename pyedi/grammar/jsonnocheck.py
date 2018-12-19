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
from .json import Json


class JsonNoCheck(Json):
    defaultsyntax = {
        "charset": "utf-8",
        "checkcharsetin": "strict",  # strict, ignore or botsreplace (replace with char as set in bots.ini).
        "checkcharsetout": "strict",  # strict, ignore or botsreplace (replace with char as set in bots.ini).
        "checkunknownentities": False,
        "contenttype": "application/json",
        "decimaal": ".",
        "defaultBOTSIDroot": "ROOT",
        "envelope": "",
        "indented": False,  # False:  output is one string (no cr/lf); True: output is indented/human readable
        "merge": False,
        "triad": "",
        # settings needed as defaults, but not useful for this editype
        "add_crlfafterrecord_sep": "",
        "escape": "",
        "field_sep": "",
        "forcequote": 0,  # csv only
        "quote_char": "",
        "record_sep": "",
        "record_tag_sep": "",  # Tradacoms/GTDI
        "reserve": "",
        "sfield_sep": "",
        "skip_char": "",
        # bots internal, never change/overwrite
        "has_structure": False,  # is True, read structure, recorddef, check these
        "checkcollision": False,
        "lengthnumericbare": False,
        "stripfield_sep": False,
    }