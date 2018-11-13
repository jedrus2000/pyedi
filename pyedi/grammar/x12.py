from pyedi.botslib.consts import BFORMAT, FORMAT, DECIMALS
from .grammar import Grammar


class X12(Grammar):
    defaultsyntax = {
        "add_crlfafterrecord_sep": "\r\n",
        "charset": "us-ascii",
        "checkcharsetin": "strict",  # strict, ignore or botsreplace (replace with char as set in bots.ini).
        "checkcharsetout": "strict",  # strict, ignore or botsreplace (replace with char as set in bots.ini).
        "contenttype": "application/X12",
        "decimaal": ".",
        "envelope": "x12",
        "escape": "",
        "field_sep": "*",
        "functionalgroup": "XX",
        "merge": True,
        "record_sep": "~",
        "replacechar": "",  # if separator found, replace by this character; if replacechar is an empty string: raise error
        "reserve": "^",
        "sfield_sep": ">",  # advised '\'?
        "skip_char": "\r\n",
        "version": "00403",
        "ISA01": "00",
        "ISA02": "          ",
        "ISA03": "00",
        "ISA04": "          ",
        "ISA05": "01",
        "ISA07": "01",
        "ISA11": "U",  # since ISA version 00403 this is the reserve/repetition separator. Bots does not use this anymore for ISA version >00403
        "ISA14": "1",
        "ISA15": "P",
        "GS07": "X",
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
    formatconvert = {
        "AN": "A",
        "DT": "D",
        "TM": "T",
        "N": "I",
        "N0": "I",
        "N1": "I",
        "N2": "I",
        "N3": "I",
        "N4": "I",
        "N5": "I",
        "N6": "I",
        "N7": "I",
        "N8": "I",
        "N9": "I",
        "R": "R",
        "B": "A",
        "ID": "A",
    }

    def _manipulatefieldformat(self, field, recordid):
        super(X12, self)._manipulatefieldformat(field, recordid)
        if field[BFORMAT] == "I":
            if field[FORMAT][1:]:
                field[DECIMALS] = int(field[FORMAT][1])
            else:
                field[DECIMALS] = 0