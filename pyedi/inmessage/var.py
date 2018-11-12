try:
    from xml.etree import cElementTree as ET
except ImportError:
    from xml.etree import ElementTree as ET

from gettext import gettext as _

# bots-modules

from pyedi.botslib.consts import *
from pyedi.botslib import (
    InMessageError,
)
from .inmessage import InMessage


class Var(InMessage):
    """ abstract class for edi-objects with records of variabele length."""

    def _lex(self):
        """ lexes file with variable records to list of lex_records, fields and subfields (build self.lex_records)."""
        record_sep = self.ta_info["record_sep"]
        mode_inrecord = (
            0
        )  # 1 indicates: lexing in record, 0 is lexing 'between records'.
        # for tradacoms; field_sep and record_tag_sep have same function.
        field_sep = self.ta_info["field_sep"] + self.ta_info["record_tag_sep"]
        sfield_sep = self.ta_info["sfield_sep"]
        rep_sep = self.ta_info["reserve"]
        allow_spaces_between_records = self.ta_info.get(
            "allow_spaces_between_records", True
        )
        sfield = 0  # 1: subfield, 0: not a subfield, 2:repeat
        quote_char = self.ta_info[
            "quote_char"
        ]  # typical fo csv. example with quote_char ":  ,"1523",TEXT,"123",
        mode_quote = 0  # 0=not in quote, 1=in quote
        # status within mode_quote. 0=just another char within quote, 1=met 2nd
        # quote char; might be end of quote OR escaping of another quote-char.
        mode_2quote = 0
        escape = self.ta_info[
            "escape"
        ]  # char after escape-char is not interpreted as separator
        mode_escape = 0  # 0=not escaping, 1=escaping
        # chars to ignore/skip/discard. eg edifact: if wrapped to 80pos lines and <CR/LF> at end of segment
        skip_char = self.ta_info["skip_char"]
        lex_record = []  # gather the content of a record
        value = ""  # gather the content of (sub)field; the current token
        valueline = 1  # record line of token
        valuepos = 1  # record position of token in line
        countline = 1  # count number of lines; start with 1
        countpos = 0  # count position/number of chars within line
        sep = field_sep + sfield_sep + record_sep + escape + rep_sep

        for char in self.rawinput:  # get next char
            if char == "\n":
                # count number lines/position; no action.
                countline += 1  # count line
                countpos = 0  # position back to 0
            else:
                countpos += 1  # position within line
            if mode_quote:
                # lexing within a quote; note that quote-char works as escape-char within a quote
                if mode_2quote:
                    mode_2quote = 0
                    if (
                            char == quote_char
                    ):  # after quote-char another quote-char: used to escape quote_char:
                        value += char  # append quote_char
                        continue
                    else:  # quote is ended:
                        mode_quote = 0
                        # continue parsing of this char
                elif mode_escape:  # tricky: escaping a quote char
                    mode_escape = 0
                    value += char
                    continue
                elif (
                        char == quote_char
                ):  # either end-quote or escaping quote_char,we do not know yet
                    mode_2quote = 1
                    continue
                elif char == escape:
                    mode_escape = 1
                    continue
                else:  # we are in quote, just append char to token
                    value += char
                    continue
            if char in skip_char:
                # char is skipped. In csv these chars could be in a quote; in eg edifact
                # chars will be skipped, even if after escape sign.
                continue
            if not mode_inrecord:
                # get here after record-separator is found. we are 'between' records.
                # some special handling for whtiespace characters; for other chars: go on lexing
                if char.isspace():  # whitespace = ' \t\n\r\v\f'
                    if (
                            allow_spaces_between_records
                    ):  # by default True; False for strict handling of x12/edifact
                        # exception for tab-delimited csv files. If first field is not filled:
                        # first TAB is ignored, which is not OK. Patch this:
                        if char in field_sep and self.__class__.__name__ == 'Csv': #  isinstance(self, Csv):
                            pass  # do not ignore TAB -> go on lexing
                        else:
                            continue  # ignore whitespace character; continue for-loop with next character
                    else:  # for strict checks: no spaces between records
                        raise InMessageError(
                            _(
                                "[A67]: Found space characters between segments. Line %(countline)s, position %(pos)s, position %(countpos)s."
                            ),
                            {"countline": countline, "countpos": countpos},
                        )
                mode_inrecord = 1  # not whitespace - a new record has started
            if mode_escape:
                # in escaped_mode: char after escape sign is appended to token
                mode_escape = 0
                value += char
                continue
            if not value:
                # if no char in token: this is a new token, get line and pos for (new) token
                valueline = countline
                valuepos = countpos
            if char == quote_char and (not value or value.isspace()):
                # for csv: handle new quote value. New quote value only makes sense for
                # new field (value is empty) or field contains only whitespace
                mode_quote = 1
                continue
            if char not in sep:
                value += char  # just a char: append char to value
                continue
            if char in field_sep:
                # end of (sub)field. Note: first field of composite is marked as 'field'
                lex_record.append(
                    {VALUE: value, SFIELD: sfield, LIN: valueline, POS: valuepos}
                )  # write current value to lex_record
                value = ""
                sfield = 0  # new token is field
                continue
            if char == sfield_sep:
                # end of (sub)field. Note: first field of composite is marked as 'field'
                lex_record.append(
                    {VALUE: value, SFIELD: sfield, LIN: valueline, POS: valuepos}
                )  # write current value to lex_record
                value = ""
                sfield = 1  # new token is sub-field
                continue
            if char in record_sep:  # end of record
                lex_record.append(
                    {VALUE: value, SFIELD: sfield, LIN: valueline, POS: valuepos}
                )  # write current value to lex_record
                self.lex_records.append(
                    lex_record
                )  # write lex_record to self.lex_records
                lex_record = []
                value = ""
                sfield = 0  # new token is field
                mode_inrecord = 0  # we are not in a record
                continue
            if char == escape:
                mode_escape = 1
                continue
            if char == rep_sep:
                lex_record.append(
                    {VALUE: value, SFIELD: sfield, LIN: valueline, POS: valuepos}
                )  # write current value to lex_record
                value = ""
                sfield = 2  # new token is repeating
                continue
        # end of for-loop. all characters have been processed.
        # in a perfect world, value should always be empty now, but:
        # it appears a csv record is not always closed properly, so force the closing of the last record of csv file:
        if mode_inrecord and self.ta_info.get(
                "allow_lastrecordnotclosedproperly", False
        ):
            lex_record.append(
                {VALUE: value, SFIELD: sfield, LIN: valueline, POS: valuepos}
            )  # append element in record
            self.lex_records.append(lex_record)  # write record to recordlist
        else:
            leftover = value.strip("\x00\x1a")
            if leftover:
                raise InMessageError(
                    _(
                        '[A51]: Found non-valid data at end of edi file; probably a problem with separators or message structure: "%(leftover)s".'
                    ),
                    {"leftover": leftover},
                )

    def _parsefields(self, lex_record, record_definition):
        """ Identify the fields in inmessage-record using the record_definition from the grammar
            Build a record (dictionary; field-IDs are unique within record) and return this.
        """
        list_of_fields_in_record_definition = record_definition[FIELDS]
        if record_definition[ID] == "ISA" and self.__class__.__name__ == 'X12': #  isinstance(self, X12):  # isa is an exception: no strip()
            is_x12_ISA = True
        else:
            is_x12_ISA = False
        record2build = (
            {}
        )  # record that is build from lex_record using ID's from record_definition
        tindex = -1  # elementcounter; composites count as one
        # ~ tsubindex = 0     #sub-element counter within composite; for files that are OK: init when compostie is detected. This init is for error (field is lexed as subfield but is not.) 20130222: catch UnboundLocalError now
        # ********loop over all fields present in this record of edi file
        # ********identify the lexed fields in grammar, and build a dict with (fieldID:value)
        for lex_field in lex_record:
            value = lex_field[VALUE].strip() if not is_x12_ISA else lex_field[VALUE][:]
            # *********use info of lexer: what is preceding separator (field, sub-field, repeat)
            if not lex_field[SFIELD]:  # preceded by field-separator
                try:
                    tindex += 1  # use next field
                    field_definition = list_of_fields_in_record_definition[tindex]
                except IndexError:
                    self.add2errorlist(
                        _(
                            '[F19] line %(line)s pos %(pos)s: Record "%(record)s" too many fields in record; unknown field "%(content)s".\n'
                        )
                        % {
                            "content": lex_field[VALUE],
                            "line": lex_field[LIN],
                            "pos": lex_field[POS],
                            "record": self.mpathformat(record_definition[MPATH]),
                        }
                    )
                    continue
                if field_definition[MAXREPEAT] == 1:  # definition says: not repeating
                    if field_definition[ISFIELD]:  # definition says: field       +E+
                        if value:
                            record2build[field_definition[ID]] = value
                    else:  # definition says: subfield    +E:S+
                        tsubindex = 0
                        list_of_subfields_in_record_definition = list_of_fields_in_record_definition[
                            tindex
                        ][
                            SUBFIELDS
                        ]
                        sub_field_in_record_definition = list_of_subfields_in_record_definition[
                            tsubindex
                        ]
                        if value:
                            record2build[sub_field_in_record_definition[ID]] = value
                else:  # definition says: repeating
                    if field_definition[ISFIELD]:  # definition says: field      +E*R+
                        record2build[field_definition[ID]] = [value]
                    else:  # definition says: subfield   +E:S*R:S+
                        tsubindex = 0
                        list_of_subfields_in_record_definition = list_of_fields_in_record_definition[
                            tindex
                        ][
                            SUBFIELDS
                        ]
                        sub_field_in_record_definition = list_of_subfields_in_record_definition[
                            tsubindex
                        ]
                        record2build[field_definition[ID]] = [
                            {sub_field_in_record_definition[ID]: value}
                        ]
            elif lex_field[SFIELD] == 1:  # preceded by sub-field separator
                try:
                    tsubindex += 1
                    sub_field_in_record_definition = list_of_subfields_in_record_definition[
                        tsubindex
                    ]
                except (
                        TypeError,
                        UnboundLocalError,
                ):  # field has no SUBFIELDS, or unexpected subfield
                    self.add2errorlist(
                        _(
                            '[F17] line %(line)s pos %(pos)s: Record "%(record)s" expect field but "%(content)s" is a subfield.\n'
                        )
                        % {
                            "content": lex_field[VALUE],
                            "line": lex_field[LIN],
                            "pos": lex_field[POS],
                            "record": self.mpathformat(record_definition[MPATH]),
                        }
                    )
                    continue
                except IndexError:  # tsubindex is not in the subfields
                    self.add2errorlist(
                        _(
                            '[F18] line %(line)s pos %(pos)s: Record "%(record)s" too many subfields in composite; unknown subfield "%(content)s".\n'
                        )
                        % {
                            "content": lex_field[VALUE],
                            "line": lex_field[LIN],
                            "pos": lex_field[POS],
                            "record": self.mpathformat(record_definition[MPATH]),
                        }
                    )
                    continue
                if (
                        field_definition[MAXREPEAT] == 1
                ):  # definition says: not repeating   +E:S+
                    if value:
                        record2build[sub_field_in_record_definition[ID]] = value
                else:  # definition says: repeating       +E:S*R:S+
                    record2build[field_definition[ID]][-1][
                        sub_field_in_record_definition[ID]
                    ] = value
            else:  # preceded by repeat separator
                # check if repeating!
                if field_definition[MAXREPEAT] == 1:
                    # exception for ISA
                    if (
                            "ISA" == self.mpathformat(record_definition[MPATH])
                            and field_definition[ID] == "ISA11"
                    ):
                        pass
                    else:
                        self.add2errorlist(
                            _(
                                '[F40] line %(line)s pos %(pos)s: Record "%(record)s" expect not-repeating elemen, but "%(content)s" is repeating.\n'
                            )
                            % {
                                "content": lex_field[VALUE],
                                "line": lex_field[LIN],
                                "pos": lex_field[POS],
                                "record": self.mpathformat(record_definition[MPATH]),
                            }
                        )
                    continue

                if field_definition[ISFIELD]:  # definition says: field      +E*R+
                    record2build[field_definition[ID]].append(value)
                else:  # definition says: first subfield   +E:S*R:S+
                    tsubindex = 0
                    list_of_subfields_in_record_definition = list_of_fields_in_record_definition[
                        tindex
                    ][
                        SUBFIELDS
                    ]
                    sub_field_in_record_definition = list_of_subfields_in_record_definition[
                        tsubindex
                    ]
                    record2build[field_definition[ID]].append(
                        {sub_field_in_record_definition[ID]: value}
                    )
        record2build["BOTSIDnr"] = record_definition[BOTSIDNR]
        return record2build

    @staticmethod
    def separatorcheck(separatorstring):
        """check if separators are 'reasonable':
        """
        # test uniqueness
        if len(separatorstring) != len(set(separatorstring)):
            raise Exception(
                _("[A64]: Separator problem in edi file: overlapping separators.")
            )
        # test if a space
        if " " in separatorstring:
            raise Exception(
                _(
                    "[A65]: Separator problem in edi file: space is used as an separator."
                )
            )
        # check if separators are alfanumeric
        for sep in separatorstring:
            if sep.isalnum():
                raise Exception(
                    _(
                        "[A66]: Separator problem in edi file: found alfanumeric separator."
                    )
                )


