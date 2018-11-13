# -*- coding: utf-8 -*-
import time
import decimal

NODECIMAL = decimal.Decimal(1)

from gettext import gettext as _

try:
    from xml.etree import cElementTree as ET
except ImportError:
    from xml.etree import ElementTree as ET

try:
    import elementtree.ElementInclude as ETI
except ImportError:
    from xml.etree import ElementInclude as ETI

from pyedi.botslib.consts import *
from pyedi.botslib import (
    OutMessageError,
    opendata,
    get_relevant_text_for_UnicodeError,
    BotsImportError,
    logger,
)
import pyedi.node as node
import pyedi.message as message
import pyedi.grammar as grammar


class OutMessage(message.Message):
    """ abstract class; represents a outgoing edi message.
        subclassing is necessary for the editype (csv, edi, x12, etc)
        A tree of nodes is build form the mpaths received from put()or putloop(). tree starts at self.root.
        Put() recieves mpaths from mappingscript
        The next algorithm is used to 'map' a mpath into the tree:
            For each part of a mpath: search node in 'current' level of tree
                If part already as a node:
                    recursively search node-children
                If part not as a node:
                    append new node to tree;
                    recursively append next parts to tree
        After the mappingscript is finished, the resulting tree is converted to self.lex_records.
        These lex_records are written to file.
    """

    def __init__(self, ta_info):
        super(OutMessage, self).__init__(ta_info)
        # message tree; build via put()-interface in mappingscript. Initialise with empty dict
        self.root = node.Node(record={})

    def messagegrammarread(self, typeofgrammarfile):
        """ read grammar for a message/envelope.
            (try to) read the topartner dependent grammar syntax.
        """
        super(OutMessage, self).messagegrammarread(typeofgrammarfile)
        # read partner-syntax. Use this to always overrule values in self.ta_info
        if self.ta_info.get("frompartner"):
            try:
                partnersyntax = grammar.grammarread(
                    self.ta_info["editype"],
                    self.ta_info["frompartner"],
                    typeofgrammarfile="partners",
                )
                self.ta_info.update(partnersyntax.syntax)  # partner syntax overrules!
            except BotsImportError:
                pass  # No partner specific syntax found (is not an error).
        if self.ta_info.get("topartner"):
            try:
                partnersyntax = grammar.grammarread(
                    self.ta_info["editype"],
                    self.ta_info["topartner"],
                    typeofgrammarfile="partners",
                )
                self.ta_info.update(partnersyntax.syntax)  # partner syntax overrules!
            except BotsImportError:
                pass  # No partner specific syntax found (is not an error).

    def writeall(self):
        """ writeall is called for writing all 'real' outmessage objects; but not for envelopes.
            writeall is call from transform.translate()
        """
        self.messagegrammarread(typeofgrammarfile="grammars")
        self.checkmessage(self.root, self.defmessage)
        self.checkforerrorlist()
        self.nrmessagewritten = 0
        if (
            self.root.record
        ):  # root record contains information; write whole tree in one time
            self.multiplewrite = False
            self._initwrite()
            self._write(self.root)
            self.nrmessagewritten = 1
            self.ta_info["nrmessages"] = self.nrmessagewritten
            self._closewrite()
        elif not self.root.children:
            raise OutMessageError(
                _("No outgoing message")
            )  # then there is nothing to write...
        else:
            self.multiplewrite = True
            self._initwrite()
            for childnode in self.root.children:
                self._write(childnode)
                self.nrmessagewritten += 1
            #'write back' the number of messages. Tricky thing here is that sometimes such a structure is indeed one message: eg csv without BOTS iD.
            # in general: when only one type of record in recorddefs (mind: for xml this is not useful) no not writeback the count as nrofmessages
            # for now: always write back unless csv of fixed.
            if self.__class__.__name__ not in ['Csv', 'Fixed']:
                self.ta_info["nrmessages"] = self.nrmessagewritten
            self._closewrite()

    def _initwrite(self):
        logger.debug('Start writing to file "%(filename)s".', self.ta_info)
        self._outstream = opendata(
            self.ta_info["filename"],
            "wb",
            charset=self.ta_info["charset"],
            errors=self.ta_info["checkcharsetout"],
        )

    def _closewrite(self):
        logger.debug('End writing to file "%(filename)s".', self.ta_info)
        self._outstream.close()

    def _write(self, node_instance):
        """ the write method for most classes.
            tree is serialised to lex_records; lex_records are written to file.
            Classses that write using other libraries (xml, json, template, db) use specific write methods.
        """
        self.tree2records(node_instance)
        value = self.record2string(self.lex_records)
        wrap_length = int(self.ta_info.get("wrap_length", 0))
        if wrap_length:
            try:
                for i in range(0, len(value), wrap_length):  # split in fixed lengths
                    self._outstream.write(value[i : i + wrap_length] + "\r\n")
            except UnicodeError as msg:
                content = get_relevant_text_for_UnicodeError(msg)
                raise OutMessageError(
                    _('[F50]: Characters not in character-set "%(char)s": %(content)s'),
                    {"char": self.ta_info["charset"], "content": content},
                )
        else:
            try:
                self._outstream.write(value)
            except UnicodeError as msg:
                content = get_relevant_text_for_UnicodeError(msg)
                raise OutMessageError(
                    _('[F50]: Characters not in character-set "%(char)s": %(content)s'),
                    {"char": self.ta_info["charset"], "content": content},
                )

    def tree2records(self, node_instance):
        self.lex_records = []  # tree of nodes is flattened to these lex_records
        self._tree2recordscore(node_instance, self.defmessage.structure[0])

    def _tree2recordscore(self, node_instance, structure):
        """ Write tree of nodes to flat lex_records.
            The nodes are already sorted
        """
        self._tree2recordfields(
            node_instance.record, structure
        )  # write node->lex_record
        for childnode in node_instance.children:
            botsid_childnode = childnode.record[
                "BOTSID"
            ].strip()  # speed up: use local var
            botsidnr_childnode = childnode.record["BOTSIDnr"]  # speed up: use local var
            for structure_record in structure[
                LEVEL
            ]:  # for structure_record of this level in grammar
                # check if is is the right node
                if (
                    botsid_childnode == structure_record[ID]
                    and botsidnr_childnode == structure_record[BOTSIDNR]
                ):
                    self._tree2recordscore(
                        childnode, structure_record
                    )  # use rest of index in deeper level
                    break  # childnode was found and used; break to go to next child node

    def _tree2recordfields(self, noderecord, structure_record):
        """ from noderecord->lex_record; use structure_record as guide.
            complex because is is used for: editypes that have compression rules (edifact), var editypes without compression, fixed protocols
        """
        lex_record = []  # the record build; list (=record) of dicts (=fields).
        recordbuffer = []
        for field_definition in structure_record[
            FIELDS
        ]:  # loop all fields in grammar-definition
            if field_definition[ISFIELD]:  # if field (no composite)
                if field_definition[MAXREPEAT] == 1:  # if non-repeating
                    field_has_data = False
                    if (
                        field_definition[ID] in noderecord
                        and noderecord[field_definition[ID]]
                    ):
                        # field exists in outgoing message and has data
                        field_has_data = True
                        recordbuffer.append(
                            {
                                VALUE: noderecord[field_definition[ID]],
                                SFIELD: 0,
                                FORMATFROMGRAMMAR: field_definition[FORMAT],
                            }
                        )
                    elif self.ta_info["stripfield_sep"]:
                        # no data and field not needed: write new empty field to recordbuffer;
                        recordbuffer.append(
                            {
                                VALUE: "",
                                SFIELD: 0,
                                FORMATFROMGRAMMAR: field_definition[FORMAT],
                            }
                        )
                    else:
                        # no data but field is needed: initialise empty field. For eg fixed and
                        # csv: all fields have to be present
                        field_has_data = True
                        value = self._initfield(field_definition)
                        recordbuffer.append(
                            {
                                VALUE: value,
                                SFIELD: 0,
                                FORMATFROMGRAMMAR: field_definition[FORMAT],
                            }
                        )
                    if field_has_data:
                        lex_record += recordbuffer  # write recordbuffer to lex_record
                        recordbuffer = []  # clear recordbuffer
                else:  # repeating field
                    field_has_data = False
                    if (
                        field_definition[ID] in noderecord
                    ):  # field exists in outgoing message
                        type_of_field = (
                            0
                        )  # first field in repeat is marked as a field (not as repeat).
                        fieldbuffer = []  # buffer for this repeating field.
                        for field in noderecord[field_definition[ID]]:
                            if field:
                                field_has_data = True
                                fieldbuffer.append(
                                    {
                                        VALUE: field,
                                        SFIELD: type_of_field,
                                        FORMATFROMGRAMMAR: field_definition[FORMAT],
                                    }
                                )
                                recordbuffer += fieldbuffer
                                fieldbuffer = []
                            else:
                                fieldbuffer.append(
                                    {
                                        VALUE: "",
                                        SFIELD: type_of_field,
                                        FORMATFROMGRAMMAR: field_definition[FORMAT],
                                    }
                                )
                            type_of_field = 2  # mark rest of repeats as repeat.
                    if field_has_data:
                        lex_record += recordbuffer  # write recordbuffer to lex_record
                        recordbuffer = []  # clear recordbuffer
                    else:
                        recordbuffer.append(
                            {
                                VALUE: "",
                                SFIELD: 0,
                                FORMATFROMGRAMMAR: field_definition[FORMAT],
                            }
                        )
            else:  # if composite
                if field_definition[MAXREPEAT] == 1:  # if non-repeating
                    field_has_data = False
                    type_of_field = (
                        0
                    )  # first subfield in composite is marked as a field (not a subfield).
                    fieldbuffer = []  # buffer for this composite.
                    for grammarsubfield in field_definition[
                        SUBFIELDS
                    ]:  # loop subfields
                        # field exists in outgoing message and has data
                        if (
                            grammarsubfield[ID] in noderecord
                            and noderecord[grammarsubfield[ID]]
                        ):
                            field_has_data = True
                            fieldbuffer.append(
                                {
                                    VALUE: noderecord[grammarsubfield[ID]],
                                    SFIELD: type_of_field,
                                }
                            )  # append field
                            recordbuffer += fieldbuffer
                            fieldbuffer = []
                        else:
                            fieldbuffer.append(
                                {VALUE: "", SFIELD: type_of_field}
                            )  # append new empty to buffer;
                        type_of_field = 1
                    if field_has_data:
                        lex_record += recordbuffer  # write recordbuffer to lex_record
                        recordbuffer = []  # clear recordbuffer
                    else:
                        # composite has no data: write empty field
                        recordbuffer.append({VALUE: "", SFIELD: 0})
                else:  # repeating composite
                    # receive list, including empty members
                    field_has_data = False
                    if (
                        field_definition[ID] in noderecord
                    ):  # field exists in outgoing message
                        type_of_field = (
                            0
                        )  # first subfield in composite is marked as a field (not a subfield).
                        fieldbuffer = []  # buffer for this composite.
                        for comp_dict in noderecord[field_definition[ID]]:
                            composite_has_data = False  # comp_dict can be empty
                            compositebuffer = []  # buffer for this composite.
                            if comp_dict:
                                for grammarsubfield in field_definition[
                                    SUBFIELDS
                                ]:  # loop subfields
                                    # field exists in outgoing message and has data
                                    if (
                                        grammarsubfield[ID] in comp_dict
                                        and comp_dict[grammarsubfield[ID]]
                                    ):
                                        composite_has_data = True
                                        compositebuffer.append(
                                            {
                                                VALUE: comp_dict[grammarsubfield[ID]],
                                                SFIELD: type_of_field,
                                                FORMATFROMGRAMMAR: grammarsubfield[
                                                    FORMAT
                                                ],
                                            }
                                        )
                                        fieldbuffer += compositebuffer
                                        compositebuffer = []
                                    else:
                                        compositebuffer.append(
                                            {
                                                VALUE: "",
                                                SFIELD: type_of_field,
                                                FORMATFROMGRAMMAR: grammarsubfield[
                                                    FORMAT
                                                ],
                                            }
                                        )
                                    type_of_field = 1
                            if composite_has_data:
                                field_has_data = True
                                recordbuffer += fieldbuffer
                                fieldbuffer = []
                            else:
                                fieldbuffer.append({VALUE: "", SFIELD: type_of_field})
                            type_of_field = 2
                    if field_has_data:
                        lex_record += recordbuffer  # write recordbuffer to lex_record
                        recordbuffer = []  # clear recordbuffer
                    else:
                        # no data: write placeholder to recordbuffer;
                        recordbuffer.append({VALUE: "", SFIELD: 0})

        self.lex_records.append(lex_record)

    def _formatfield(self, value, field_definition, structure_record, node_instance):
        """ Input: value (as a string) and field definition.
            Some parameters of self.syntax are used, eg decimaal
            Format is checked and converted (if needed).
            return the formatted value
        """
        if field_definition[BFORMAT] == "A":
            if self.__class__.__name__ == 'Fixed':  # check length fields in variable records
                if (
                    field_definition[FORMAT] == "AR"
                ):  # if field format is alfanumeric right aligned
                    value = value.rjust(field_definition[MINLENGTH])
                else:
                    # add spaces (left, because A-field is right aligned)
                    value = value.ljust(field_definition[MINLENGTH])
            if len(value) > field_definition[LENGTH]:
                self.add2errorlist(
                    _(
                        '[F20]: Record "%(record)s" field "%(field)s" too big (max %(max)s): "%(content)s".\n'
                    )
                    % {
                        "record": self.mpathformat(structure_record[MPATH]),
                        "field": field_definition[ID],
                        "content": value,
                        "max": field_definition[LENGTH],
                    }
                )
            if len(value) < field_definition[MINLENGTH]:
                self.add2errorlist(
                    _(
                        '[F21]: Record "%(record)s" field "%(field)s" too small (min %(min)s): "%(content)s".\n'
                    )
                    % {
                        "record": self.mpathformat(structure_record[MPATH]),
                        "field": field_definition[ID],
                        "content": value,
                        "min": field_definition[MINLENGTH],
                    }
                )
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
                            '[F22]: Record "%(record)s" date field "%(field)s" not a valid date: "%(content)s".\n'
                        )
                        % {
                            "record": self.mpathformat(structure_record[MPATH]),
                            "field": field_definition[ID],
                            "content": value,
                        }
                    )
                if lenght > field_definition[LENGTH]:
                    self.add2errorlist(
                        _(
                            '[F31]: Record "%(record)s" date field "%(field)s" too big (max %(max)s): "%(content)s".\n'
                        )
                        % {
                            "record": self.mpathformat(structure_record[MPATH]),
                            "field": field_definition[ID],
                            "content": value,
                            "max": field_definition[LENGTH],
                        }
                    )
                if lenght < field_definition[MINLENGTH]:
                    self.add2errorlist(
                        _(
                            '[F32]: Record "%(record)s" date field "%(field)s" too small (min %(min)s): "%(content)s".\n'
                        )
                        % {
                            "record": self.mpathformat(structure_record[MPATH]),
                            "field": field_definition[ID],
                            "content": value,
                            "min": field_definition[MINLENGTH],
                        }
                    )
            else:  # if field_definition[BFORMAT] == 'T':
                try:
                    if lenght == 4:
                        time.strptime(value, "%H%M")
                    elif lenght == 6:
                        time.strptime(value, "%H%M%S")
                    else:
                        raise ValueError("To be catched")
                except ValueError:
                    self.add2errorlist(
                        _(
                            '[F23]: Record "%(record)s" time field "%(field)s" not a valid time: "%(content)s".\n'
                        )
                        % {
                            "record": self.mpathformat(structure_record[MPATH]),
                            "field": field_definition[ID],
                            "content": value,
                        }
                    )
                if lenght > field_definition[LENGTH]:
                    self.add2errorlist(
                        _(
                            '[F33]: Record "%(record)s" time field "%(field)s" too big (max %(max)s): "%(content)s".\n'
                        )
                        % {
                            "record": self.mpathformat(structure_record[MPATH]),
                            "field": field_definition[ID],
                            "content": value,
                            "max": field_definition[LENGTH],
                        }
                    )
                if lenght < field_definition[MINLENGTH]:
                    self.add2errorlist(
                        _(
                            '[F34]: Record "%(record)s" time field "%(field)s" too small (min %(min)s): "%(content)s".\n'
                        )
                        % {
                            "record": self.mpathformat(structure_record[MPATH]),
                            "field": field_definition[ID],
                            "content": value,
                            "min": field_definition[MINLENGTH],
                        }
                    )
        else:  # numerics
            # ~ if value[0] == '-':
            # ~ minussign = '-'
            # ~ absvalue = value[1:]
            # ~ else:
            # ~ minussign = ''
            # ~ absvalue = value
            # ~ digits,decimalsign,decimals = absvalue.partition('.')
            # ~ if not digits:
            # ~ digits = '0'
            # ~ if not decimals:# and decimalsign:
            # ~ self.add2errorlist(_('[F24]: Record "%(record)s" field "%(field)s" numerical format not valid: "%(content)s".\n')%
            # ~ {'field':field_definition[ID],'content':value,'record':self.mpathformat(structure_record[MPATH])})

            # for some formats (if self.ta_info['lengthnumericbare']=True; eg edifact)
            # length is calculated without decimal sing and/or minus sign.
            lengthcorrection = 0
            if (
                field_definition[BFORMAT] == "R"
            ):  # floating point: use all decimals received
                if self.ta_info["lengthnumericbare"]:
                    if value[0] == "-":
                        lengthcorrection += 1
                    if "." in value:
                        lengthcorrection += 1
                try:
                    value = str(decimal.Decimal(value))
                except:
                    self.add2errorlist(
                        _(
                            '[F25]: Record "%(record)s" field "%(field)s" numerical format not valid: "%(content)s".\n'
                        )
                        % {
                            "field": field_definition[ID],
                            "content": value,
                            "record": self.mpathformat(structure_record[MPATH]),
                        }
                    )
                if (
                    field_definition[FORMAT] == "RL"
                ):  # if field format is numeric left aligned
                    value = value.ljust(field_definition[MINLENGTH] + lengthcorrection)
                elif (
                    field_definition[FORMAT] == "RR"
                ):  # if field format is numeric right aligned
                    value = value.rjust(field_definition[MINLENGTH] + lengthcorrection)
                else:
                    value = value.zfill(field_definition[MINLENGTH] + lengthcorrection)
                value = value.replace(
                    ".", self.ta_info["decimaal"], 1
                )  # replace '.' by required decimal sep.
            elif field_definition[BFORMAT] == "N":  # fixed decimals; round
                if self.ta_info["lengthnumericbare"]:
                    if value[0] == "-":
                        lengthcorrection += 1
                    if field_definition[DECIMALS]:
                        lengthcorrection += 1
                try:
                    dec_value = decimal.Decimal(value)
                    value = str(
                        dec_value.quantize(
                            decimal.Decimal("10e-%d" % field_definition[DECIMALS])
                        )
                    )
                except:
                    self.add2errorlist(
                        _(
                            '[F26]: Record "%(record)s" field "%(field)s" numerical format not valid: "%(content)s".\n'
                        )
                        % {
                            "field": field_definition[ID],
                            "content": value,
                            "record": self.mpathformat(structure_record[MPATH]),
                        }
                    )
                if (
                    field_definition[FORMAT] == "NL"
                ):  # if field format is numeric left aligned
                    value = value.ljust(field_definition[MINLENGTH] + lengthcorrection)
                elif (
                    field_definition[FORMAT] == "NR"
                ):  # if field format is numeric right aligned
                    value = value.rjust(field_definition[MINLENGTH] + lengthcorrection)
                else:
                    value = value.zfill(field_definition[MINLENGTH] + lengthcorrection)
                value = value.replace(
                    ".", self.ta_info["decimaal"], 1
                )  # replace '.' by required decimal sep.
            elif field_definition[BFORMAT] == "I":  # implicit decimals
                if self.ta_info["lengthnumericbare"]:
                    if value[0] == "-":
                        lengthcorrection += 1
                try:
                    dec_value = decimal.Decimal(value).shift(field_definition[DECIMALS])
                    value = str(dec_value.quantize(NODECIMAL))
                except:
                    self.add2errorlist(
                        _(
                            '[F27]: Record "%(record)s" field "%(field)s" numerical format not valid: "%(content)s".\n'
                        )
                        % {
                            "field": field_definition[ID],
                            "content": value,
                            "record": self.mpathformat(structure_record[MPATH]),
                        }
                    )
                value = value.zfill(field_definition[MINLENGTH] + lengthcorrection)

            if len(value) - lengthcorrection > field_definition[LENGTH]:
                self.add2errorlist(
                    _(
                        '[F28]: Record "%(record)s" field "%(field)s" too big: "%(content)s".\n'
                    )
                    % {
                        "record": self.mpathformat(structure_record[MPATH]),
                        "field": field_definition[ID],
                        "content": value,
                    }
                )
        return value

    def _initfield(self, field_definition):
        """ for some editypes like fixed fields without date have specific initalisation.
            this is controlled by the 'stripfield_sep' parameter in grammar.
        """
        if field_definition[BFORMAT] in "ADT":
            value = ""
        else:  # numerics
            value = "0"
            if (
                field_definition[BFORMAT] == "R"
            ):  # floating point: use all decimals received
                value = value.zfill(field_definition[MINLENGTH])
            elif field_definition[BFORMAT] == "N":  # fixed decimals; round
                value = str(
                    decimal.Decimal(value).quantize(
                        decimal.Decimal("10e-%d" % field_definition[DECIMALS])
                    )
                )
                value = value.zfill(field_definition[MINLENGTH])
                value = value.replace(
                    ".", self.ta_info["decimaal"], 1
                )  # replace '.' by required decimal sep.
            elif field_definition[BFORMAT] == "I":  # implicit decimals
                value = value.zfill(field_definition[MINLENGTH])
        return value

    def record2string(self, lex_records):
        """ write lex_records to a file.
            using the right editype (edifact, x12, etc) and charset.
            write (all fields of) each record using the right separators, escape etc
        """
        sfield_sep = self.ta_info["sfield_sep"]
        if self.ta_info["record_tag_sep"]:
            record_tag_sep = self.ta_info["record_tag_sep"]
        else:
            record_tag_sep = self.ta_info["field_sep"]
        field_sep = self.ta_info["field_sep"]
        quote_char = self.ta_info["quote_char"]
        escape = self.ta_info["escape"]
        record_sep = (
            self.ta_info["record_sep"] + self.ta_info["add_crlfafterrecord_sep"]
        )
        forcequote = self.ta_info["forcequote"]
        escapechars = self._getescapechars()
        noBOTSID = self.ta_info.get("noBOTSID", False)
        rep_sep = self.ta_info["reserve"]

        lijst = []
        for lex_record in lex_records:
            if noBOTSID:  # for csv/fixed: do not write BOTSID so remove it
                del lex_record[0]
            fieldcount = 0
            mode_quote = False
            value = ""  # to collect the formatted record-string.
            for field in lex_record:  # loop all fields in lex_record
                if not field[SFIELD]:  # is a field:
                    if (
                        fieldcount == 0
                    ):  # do nothing because first field in lex_record is not preceded by a separator
                        fieldcount = 1
                    elif fieldcount == 1:
                        value += record_tag_sep
                        fieldcount = 2
                    else:
                        value += field_sep
                elif field[SFIELD] == 1:  # is a subfield:
                    value += sfield_sep
                else:  # repeat
                    value += rep_sep
                if quote_char:  # quote char only used for csv
                    start_to__quote = False
                    if forcequote == 2:
                        if field[FORMATFROMGRAMMAR] in ["AN", "A", "AR"]:
                            start_to__quote = True
                    elif forcequote:  # always quote; this catches values 1, '1', '0'
                        start_to__quote = True
                    else:
                        if (
                            field_sep in field[VALUE]
                            or quote_char in field[VALUE]
                            or record_sep in field[VALUE]
                        ):
                            start_to__quote = True
                    if start_to__quote:
                        value += quote_char
                        mode_quote = True
                # use escape (edifact, tradacom). For x12 is warned if content contains separator
                for char in field[VALUE]:
                    if char in escapechars:
                        if self.__class__.__name__ == 'X12':
                            if self.ta_info["replacechar"]:
                                char = self.ta_info["replacechar"]
                            else:
                                raise OutMessageError(
                                    _(
                                        '[F51]: Character "%(char)s" is used as separator in this x12 file, so it can not be used in content. Field: "%(content)s".'
                                    ),
                                    {"char": char, "content": field[VALUE]},
                                )
                        else:
                            value += escape
                    elif mode_quote and char == quote_char:
                        value += quote_char
                    value += char
                if mode_quote:
                    value += quote_char
                    mode_quote = False
            value += record_sep
            lijst.append(value)
        return "".join(lijst)

    def _getescapechars(self):
        return ""
