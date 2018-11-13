from .grammar import Grammar


class TemplateHtml(Grammar):
    defaultsyntax = {
        "charset": "utf-8",
        "checkcharsetin": "strict",  # strict, ignore or botsreplace (replace with char as set in bots.ini).
        "checkcharsetout": "strict",  # strict, ignore or botsreplace (replace with char as set in bots.ini).
        "contenttype": "text/xml",
        "decimaal": ".",
        "envelope": "templatehtml",
        "envelope-template": "",
        "merge": True,
        # settings needed as defaults, but not useful for this editype
        "add_crlfafterrecord_sep": "",
        "checkunknownentities": True,
        "escape": "",
        "field_sep": "",
        "forcequote": 0,  # csv only
        "quote_char": "",
        # to indicate what should be printed as a table with 1 row per record (instead of 1 record->1 table)
        "print_as_row": [],
        "record_sep": "",
        "record_tag_sep": "",  # Tradacoms/GTDI
        "reserve": "",
        "sfield_sep": "",
        "skip_char": "",
        "triad": "",
        # bots internal, never change/overwrite
        "has_structure": False,  # is True, read structure, recorddef, check these
        "checkcollision": False,
        "lengthnumericbare": False,
        "stripfield_sep": False,
    }