from gettext import gettext as _

from pyedi.botslib import GrammarError
from .grammar import Grammar


class Csv(Grammar):
    def class_specific_tests(self):
        if self.syntax["noBOTSID"] and len(self.recorddefs) != 2:
            raise GrammarError(
                _(
                    'Grammar "%(grammar)s": if syntax["noBOTSID"]: there can be only one record in recorddefs.'
                ),
                {"grammar": self.grammarname},
            )
        if self.nextmessageblock is not None and len(self.recorddefs) != 2:
            raise GrammarError(
                _(
                    'Grammar "%(grammar)s": if nextmessageblock: there can be only one record in recorddefs.'
                ),
                {"grammar": self.grammarname},
            )

    defaultsyntax = {
        "add_crlfafterrecord_sep": "",
        # in csv sometimes the last record is no closed correctly. This is related
        # to communciation over email. Beware: when using this, other checks will
        # not be enforced!
        "allow_lastrecordnotclosedproperly": False,
        "charset": "utf-8",
        "checkcharsetin": "strict",  # strict, ignore or botsreplace (replace with char as set in bots.ini).
        "checkcharsetout": "strict",  # strict, ignore or botsreplace (replace with char as set in bots.ini).
        "contenttype": "text/csv",
        "decimaal": ".",
        "envelope": "",
        "escape": "",
        "field_sep": ":",
        # (if quote_char is set) 0:no force: only quote if necessary:1:always force: 2:quote if alfanumeric
        "forcequote": 1,
        "merge": True,
        "noBOTSID": False,  # allow csv records without record ID.
        # (csv only) if only one recordtype and no nextmessageblock: would pass record for record to mapping. this fixes that.
        "pass_all": True,
        "quote_char": "'",
        "record_sep": "\r\n",  # better is  "\n" (got some strange errors for this?)
        "skip_char": "",
        "skip_firstline": False,  # often first line in CSV is fieldnames. Usage: either False/True, or number of lines. If True, number of lines is 1
        "triad": "",
        "wrap_length": 0,  # for producing wrapped format, where a file consists of fixed length records ending with crr/lf. Often seen in mainframe, as400
        # settings needed as defaults, but not useful for this editype
        "checkunknownentities": True,
        "record_tag_sep": "",  # Tradacoms/GTDI
        "reserve": "",
        "sfield_sep": "",
        # bots internal, never change/overwrite
        "has_structure": True,  # is True, read structure, recorddef, check these
        "checkcollision": True,
        "lengthnumericbare": False,
        "stripfield_sep": False,
    }