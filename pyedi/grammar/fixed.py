from gettext import gettext as _

from pyedi.botslib import GrammarError
from pyedi.botslib.consts import FIELDS, ID, LENGTH, FIXED_RECORD_LENGTH, LEVEL
from .grammar import Grammar


class Fixed(Grammar):
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

    formatconvert = {
        "A": "A",  # alfanumerical
        "AN": "A",  # alfanumerical
        "AR": "A",  # right aligned alfanumerical field, used in fixed records.
        "D": "D",  # date
        "DT": "D",  # date-time
        "T": "T",  # time
        "TM": "T",  # time
        "N": "N",  # numerical, fixed decimal. Fixed nr of decimals; if no decimal used: whole number, integer
        "NL": "N",  # numerical, fixed decimal. In fixed format: no preceding zeros, left aligned,
        "NR": "N",  # numerical, fixed decimal. In fixed format: preceding blancs, right aligned,
        "R": "R",  # numerical, any number of decimals; the decimal point is 'floating'
        "RL": "R",  # numerical, any number of decimals. fixed: no preceding zeros, left aligned
        "RR": "R",  # numerical, any number of decimals. fixed: preceding blancs, right aligned
        "I": "I",  # numercial, implicit decimal
    }
    defaultsyntax = {
        "charset": "us-ascii",
        "checkcharsetin": "strict",  # strict, ignore or botsreplace (replace with char as set in bots.ini).
        "checkcharsetout": "strict",  # strict, ignore or botsreplace (replace with char as set in bots.ini).
        "checkfixedrecordtoolong": True,
        "checkfixedrecordtooshort": False,
        "contenttype": "text/plain",
        "decimaal": ".",
        "envelope": "",
        "merge": True,
        "noBOTSID": False,  # allow fixed records without record ID.
        "triad": "",
        # settings needed as defaults, but not useful for this editype
        "add_crlfafterrecord_sep": "",
        "checkunknownentities": True,
        "escape": "",
        "field_sep": "",
        "forcequote": 0,  # csv only
        "quote_char": "",
        "record_sep": "\r\n",
        "record_tag_sep": "",  # Tradacoms/GTDI
        "reserve": "",
        "sfield_sep": "",
        "skip_char": "",
        # bots internal, never change/overwrite
        "has_structure": True,  # is True, read structure, recorddef, check these
        "checkcollision": True,
        "lengthnumericbare": False,
        "stripfield_sep": False,
    }
    is_first_record = True

    def _linkrecorddefs2structure(self, structure):
        """ specific for class fixed: extra check, determine position BOTSID in record
            recursive
            for each record in structure: add the pointer to the right recorddefinition.
        """
        for i in structure:
            try:
                # lookup the recordID in recorddefs (a dict); set pointer in structure to recorddefs/fields
                i[FIELDS] = self.recorddefs[i[ID]]
            except KeyError:
                _exception = GrammarError(
                    _(
                        'Grammar "%(grammar)s": record "%(record)s" is in structure but not in recorddefs.'
                    ),
                    {"grammar": self.grammarname, "record": i[ID]},
                )
                _exception.__cause__ = None
                raise _exception
            # For fixed records do extra things in _linkrecorddefs2structure:
            position_in_record = 0
            for field in i[FIELDS]:
                if field[ID] == "BOTSID":
                    if self.is_first_record:
                        # for first record: 1. determine start/end of BOTSID; this is needed when
                        # reading/parsing fixed records.
                        self.is_first_record = False
                        self.syntax["startrecordID"] = position_in_record
                        self.syntax["endrecordID"] = position_in_record + field[LENGTH]
                    else:
                        # for non-first records: 2. check if start/end of BOTSID is the same for
                        # all records; this is needed to correctly parse fixed files.
                        if (
                            self.syntax["startrecordID"] != position_in_record
                            or self.syntax["endrecordID"]
                            != position_in_record + field[LENGTH]
                        ):
                            raise GrammarError(
                                _(
                                    'Grammar "%(grammar)s", record %(key)s: position and length of BOTSID should be equal in all records.'
                                ),
                                {"grammar": self.grammarname, "key": i[ID]},
                            )
                    break
                position_in_record += field[LENGTH]
            # 3. calculate record length
            i[FIXED_RECORD_LENGTH] = sum(field[LENGTH] for field in i[FIELDS])
            if self.syntax["noBOTSID"]:  # correct record-length if noBOTSID
                i[FIXED_RECORD_LENGTH] -= -(
                    self.syntax["endrecordID"] - self.syntax["startrecordID"]
                )
            # and go recursive
            if LEVEL in i:
                self._linkrecorddefs2structure(i[LEVEL])