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