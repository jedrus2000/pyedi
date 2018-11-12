import time

try:
    from xml.etree import cElementTree as ET
except ImportError:
    from xml.etree import ElementTree as ET

from gettext import gettext as _

# bots-modules

from pyedi.botslib.consts import *
from pyedi.botslib import (
    opendata,
    get_relevant_text_for_UnicodeError,
    InMessageError,
    logger,
)

from .inmessage import InMessage


class Fixed(InMessage):
    """ class for record of fixed length."""

    def _readcontent_edifile(self):
        """ open the edi file.
        """
        logger.debug('Read edi file "%(filename)s".', self.ta_info)
        self.filehandler = opendata(
            filename=self.ta_info["filename"],
            mode="rb",
            charset=self.ta_info["charset"],
            errors=self.ta_info["checkcharsetin"],
        )

    def _lex(self):
        """ edi file->self.lex_records."""
        try:
            # there is a problem with the way python reads line by line: file/line offset is not correctly reported.
            # so the error is catched here to give correct/reasonable result.
            if self.ta_info["noBOTSID"]:  # if read records contain no BOTSID: add it
                botsid = self.defmessage.structure[0][
                    ID
                ]  # add the recordname as BOTSID
                for linenr, line in enumerate(self.filehandler, start=1):
                    if not line.isspace():
                        line = line.rstrip("\r\n")
                        # append record to recordlist
                        self.lex_records.append(
                            [{VALUE: botsid, LIN: linenr, POS: 0, FIXEDLINE: line}]
                        )
            else:
                startrecordid = self.ta_info["startrecordID"]
                endrecordid = self.ta_info["endrecordID"]
                for linenr, line in enumerate(self.filehandler, start=1):
                    if not line.isspace():
                        line = line.rstrip("\r\n")
                        # append record to recordlist
                        self.lex_records.append(
                            [
                                {
                                    VALUE: line[startrecordid:endrecordid].strip(),
                                    LIN: linenr,
                                    POS: 0,
                                    FIXEDLINE: line,
                                }
                            ]
                        )
        except UnicodeError as msg:
            rep_linenr = locals().get("linenr", 0) + 1
            content = get_relevant_text_for_UnicodeError(msg)
            _exception = InMessageError(
                _(
                    'Characterset problem in file. At/after line %(line)s: "%(content)s"'
                ),
                {"line": rep_linenr, "content": content},
            )
            _exception.__cause__ = None
            raise _exception

    def _parsefields(self, lex_record, record_definition):
        """ Parse fields from one fixed message-record and check length of the fixed record.
        """
        record2build = {}  # start with empty dict
        fixedrecord = lex_record[ID][FIXEDLINE]  # shortcut to fixed incoming record
        lenfixed = len(fixedrecord)
        recordlength = record_definition[FIXED_RECORD_LENGTH]
        if record_definition[FIXED_RECORD_LENGTH] != len(fixedrecord):
            if (
                    record_definition[FIXED_RECORD_LENGTH] > len(fixedrecord)
                    and self.ta_info["checkfixedrecordtooshort"]
            ):
                raise InMessageError(
                    _(
                        '[S52] line %(line)s: Record "%(record)s" too short; is %(pos)s pos, defined is %(defpos)s pos.'
                    ),
                    line=lex_record[ID][LIN],
                    record=lex_record[ID][VALUE],
                    pos=len(fixedrecord),
                    defpos=record_definition[FIXED_RECORD_LENGTH],
                )
            if (
                    record_definition[FIXED_RECORD_LENGTH] < len(fixedrecord)
                    and self.ta_info["checkfixedrecordtoolong"]
            ):
                raise InMessageError(
                    _(
                        '[S53] line %(line)s: Record "%(record)s" too long; is %(pos)s pos, defined is %(defpos)s pos.'
                    ),
                    line=lex_record[ID][LIN],
                    record=lex_record[ID][VALUE],
                    pos=len(fixedrecord),
                    defpos=record_definition[FIXED_RECORD_LENGTH],
                )
        pos = 0
        for field_definition in record_definition[FIELDS]:
            if field_definition[ID] == "BOTSID" and self.ta_info["noBOTSID"]:
                record2build["BOTSID"] = lex_record[ID][VALUE]
                continue
            value = fixedrecord[
                    pos : pos + field_definition[LENGTH]
                    ].strip()  # copy string to avoid memory problem
            if value:
                record2build[field_definition[ID]] = value
            pos += field_definition[LENGTH]
        record2build["BOTSIDnr"] = record_definition[BOTSIDNR]
        return record2build

    def _formatfield(self, value, field_definition, structure_record, node_instance):
        """ Format of a field is checked and converted if needed.
            Input: value (string), field definition.
            Output: the formatted value (string)
            Parameters of self.ta_info are used: triad, decimaal
            for fixed field: same handling; length is not checked.
        """
        if field_definition[BFORMAT] == "A":
            pass
        elif field_definition[BFORMAT] in "DT":
            lenght = len(value)
            if field_definition[BFORMAT] == "D":
                try:
                    if lenght == 6:
                        time.strptime(value, "%y%m%d")
                    elif lenght == 8:
                        time.strptime(value, "%Y%m%d")
                    else:
                        raise ValueError("To be catched")
                except ValueError:
                    self.add2errorlist(
                        _(
                            '[F07]%(linpos)s: Record "%(record)s" date field "%(field)s" not a valid date: "%(content)s".\n'
                        )
                        % {
                            "linpos": node_instance.linpos(),
                            "record": self.mpathformat(structure_record[MPATH]),
                            "field": field_definition[ID],
                            "content": value,
                        }
                    )
            else:  # if field_definition[BFORMAT] == 'T':
                try:
                    if lenght == 4:
                        time.strptime(value, "%H%M")
                    elif lenght == 6:
                        time.strptime(value, "%H%M%S")
                    elif lenght == 7 or lenght == 8:
                        time.strptime(value[0:6], "%H%M%S")
                        if not value[6:].isdigit():
                            raise ValueError("To be catched")
                    else:
                        raise ValueError("To be catched")
                except ValueError:
                    self.add2errorlist(
                        _(
                            '[F08]%(linpos)s: Record "%(record)s" time field "%(field)s" not a valid time: "%(content)s".\n'
                        )
                        % {
                            "linpos": node_instance.linpos(),
                            "record": self.mpathformat(structure_record[MPATH]),
                            "field": field_definition[ID],
                            "content": value,
                        }
                    )
        else:  # elif field_definition[BFORMAT] in 'RNI':   #numerics (R, N, I)
            if value[-1] == "-":  # if minus-sign at the end, put it in front.
                value = value[-1] + value[:-1]
            value = value.replace(self.ta_info["triad"], "")  # strip triad-separators
            value = value.replace(
                self.ta_info["decimaal"], ".", 1
            )  # replace decimal sign by canonical decimal sign
            if "E" in value or "e" in value:
                self.add2errorlist(
                    _(
                        '[F09]%(linpos)s: Record "%(record)s" field "%(field)s" contains exponent: "%(content)s".\n'
                    )
                    % {
                        "linpos": node_instance.linpos(),
                        "record": self.mpathformat(structure_record[MPATH]),
                        "field": field_definition[ID],
                        "content": value,
                    }
                )
            if field_definition[BFORMAT] == "R":
                lendecimal = len(value.partition(".")[2])
                try:  # convert to decimal in order to check validity
                    valuedecimal = float(value)
                    value = "%.*F" % (lendecimal, valuedecimal)
                except:
                    self.add2errorlist(
                        _(
                            '[F16]%(linpos)s: Record "%(record)s" numeric field "%(field)s" has non-numerical content: "%(content)s".\n'
                        )
                        % {
                            "linpos": node_instance.linpos(),
                            "record": self.mpathformat(structure_record[MPATH]),
                            "field": field_definition[ID],
                            "content": value,
                        }
                    )
            elif field_definition[BFORMAT] == "N":
                lendecimal = len(value.partition(".")[2])
                if lendecimal != field_definition[DECIMALS]:
                    self.add2errorlist(
                        _(
                            '[F14]%(linpos)s: Record "%(record)s" numeric field "%(field)s" has invalid nr of decimals: "%(content)s".\n'
                        )
                        % {
                            "linpos": node_instance.linpos(),
                            "record": self.mpathformat(structure_record[MPATH]),
                            "field": field_definition[ID],
                            "content": value,
                        }
                    )
                try:  # convert to decimal in order to check validity
                    valuedecimal = float(value)
                    value = "%.*F" % (lendecimal, valuedecimal)
                except:
                    self.add2errorlist(
                        _(
                            '[F15]%(linpos)s: Record "%(record)s" numeric field "%(field)s" has non-numerical content: "%(content)s".\n'
                        )
                        % {
                            "linpos": node_instance.linpos(),
                            "record": self.mpathformat(structure_record[MPATH]),
                            "field": field_definition[ID],
                            "content": value,
                        }
                    )
            elif field_definition[BFORMAT] == "I":
                if "." in value:
                    self.add2errorlist(
                        _(
                            '[F12]%(linpos)s: Record "%(record)s" field "%(field)s" has format "I" but contains decimal sign: "%(content)s".\n'
                        )
                        % {
                            "linpos": node_instance.linpos(),
                            "record": self.mpathformat(structure_record[MPATH]),
                            "field": field_definition[ID],
                            "content": value,
                        }
                    )
                else:
                    try:  # convert to decimal in order to check validity
                        valuedecimal = float(value)
                        valuedecimal = valuedecimal / 10 ** field_definition[DECIMALS]
                        value = "%.*F" % (field_definition[DECIMALS], valuedecimal)
                    except:
                        self.add2errorlist(
                            _(
                                '[F13]%(linpos)s: Record "%(record)s" numeric field "%(field)s" has non-numerical content: "%(content)s".\n'
                            )
                            % {
                                "linpos": node_instance.linpos(),
                                "record": self.mpathformat(structure_record[MPATH]),
                                "field": field_definition[ID],
                                "content": value,
                            }
                        )
        return value

