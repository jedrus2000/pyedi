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