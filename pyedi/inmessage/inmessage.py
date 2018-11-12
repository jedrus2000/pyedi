# -*- coding: utf-8 -*-

import sys
import time

try:
    from xml.etree import cElementTree as ET
except ImportError:
    from xml.etree import ElementTree as ET
import json as simplejson

from gettext import gettext as _

# bots-modules

from pyedi.botslib.consts import *
from pyedi.botslib import (
    globalcheckconfirmrules,
    unique,
    query,
    botsbaseimport,
    opendata,
    readdata,
    abspathdata,
    txtexc,
    get_relevant_text_for_UnicodeError,
    log_session,
    InMessageError,
    BotsError,
    BotsImportError,
    FileTooLargeError,
    checkconfirmrules,
    GotoException,
    TranslationNotFoundError,
    botsimport,
    readdata_pickled,
    readdata_bin,
    OldTransaction,
    config,
    logger,
    logmap,
    runscript,
)
import pyedi.node as node
import pyedi.message as message
import pyedi.grammar as grammar
import pyedi.outmessage as outmessage


class InMessage(message.Message):
    """ abstract class for incoming ediobject (file or message).
        Can be initialised from a file or a tree.
    """

    def __init__(self, ta_info):
        super(InMessage, self).__init__(ta_info)
        self.lex_records = []  # init list of lex_records

    def initfromfile(self):
        """ Initialisation from a edi file.
        """
        self.messagegrammarread(typeofgrammarfile="grammars")
        # **charset errors, lex errors
        # open file. variants: read with charset, read as binary & handled in sniff, only opened and read in _lex.
        self._readcontent_edifile()
        self._sniff()  # some hard-coded examination of edi file; ta_info can be overruled by syntax-parameters in edi-file
        # start lexing
        self._lex()
        # lex preprocessing via user exit indicated in syntax
        preprocess_lex = self.ta_info.get("preprocess_lex", False)
        if callable(preprocess_lex):
            preprocess_lex(lex=self.lex_records, ta_info=self.ta_info)
        if hasattr(self, "rawinput"):
            del self.rawinput
        # **breaking parser errors
        self.root = node.Node()  # make root Node None.
        self.iternext_lex_record = iter(self.lex_records)
        leftover = self._parse(
            structure_level=self.defmessage.structure, inode=self.root
        )
        if leftover:
            raise InMessageError(
                _(
                    "[A50] line %(line)s pos %(pos)s: Found non-valid data at end of edi file; probably a problem with separators or message structure."
                ),
                {"line": leftover[0][LIN], "pos": leftover[0][POS]},
            )  # probably not reached with edifact/x12 because of mailbag processing.
        del self.lex_records
        # self.root is now root of a tree (of nodes).

        # **non-breaking parser errors
        self.checkenvelope()
        self.checkmessage(self.root, self.defmessage)
        # get queries-dict for parsed message; this is used to update in database
        if self.root.record:
            self.ta_info.update(self.root.queries)
        else:
            for childnode in self.root.children:
                self.ta_info.update(childnode.queries)
                break

    def handleconfirm(self, ta_fromfile, routedict, error):
        """ end of edi file handling: writing of confirmations, etc.
        """
        pass

    def _formatfield(self, value, field_definition, structure_record, node_instance):
        """ Format of a field is checked and converted if needed.
            Input: value (string), field definition.
            Output: the formatted value (string)
            Parameters of self.ta_info are used: triad, decimaal
            for fixed field: same handling; length is not checked.
        """
        if field_definition[BFORMAT] == "A":
            if len(value) > field_definition[LENGTH]:
                self.add2errorlist(
                    _(
                        '[F05]%(linpos)s: Record "%(record)s" field "%(field)s" too big (max %(max)s): "%(content)s".\n'
                    )
                    % {
                        "linpos": node_instance.linpos(),
                        "record": self.mpathformat(structure_record[MPATH]),
                        "field": field_definition[ID],
                        "content": value,
                        "max": field_definition[LENGTH],
                    }
                )
            if len(value) < field_definition[MINLENGTH]:
                self.add2errorlist(
                    _(
                        '[F06]%(linpos)s: Record "%(record)s" field "%(field)s" too small (min %(min)s): "%(content)s".\n'
                    )
                    % {
                        "linpos": node_instance.linpos(),
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
                            '[F07]%(linpos)s: Record "%(record)s" date field "%(field)s" not a valid date: "%(content)s".\n'
                        )
                        % {
                            "linpos": node_instance.linpos(),
                            "record": self.mpathformat(structure_record[MPATH]),
                            "field": field_definition[ID],
                            "content": value,
                        }
                    )
            else:  # field_definition[BFORMAT] == 'T':
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
            if self.ta_info["lengthnumericbare"]:
                chars_not_counted = "-+" + self.ta_info["decimaal"]
                length = 0
                for c in value:
                    if c not in chars_not_counted:
                        length += 1
            else:
                length = len(value)
            if length > field_definition[LENGTH]:
                self.add2errorlist(
                    _(
                        '[F10]%(linpos)s: Record "%(record)s" field "%(field)s" too big (max %(max)s): "%(content)s".\n'
                    )
                    % {
                        "linpos": node_instance.linpos(),
                        "record": self.mpathformat(structure_record[MPATH]),
                        "field": field_definition[ID],
                        "content": value,
                        "max": field_definition[LENGTH],
                    }
                )
            if length < field_definition[MINLENGTH]:
                self.add2errorlist(
                    _(
                        '[F11]%(linpos)s: Record "%(record)s" field "%(field)s" too small (min %(min)s): "%(content)s".\n'
                    )
                    % {
                        "linpos": node_instance.linpos(),
                        "record": self.mpathformat(structure_record[MPATH]),
                        "field": field_definition[ID],
                        "content": value,
                        "min": field_definition[MINLENGTH],
                    }
                )
            if value[-1] == "-":  # if minus-sign at the end, put it in front.
                value = value[-1] + value[:-1]
            value = value.replace(self.ta_info["triad"], "")  # strip triad-separators
            value = value.replace(
                self.ta_info["decimaal"], ".", 1
            )  # replace decimal sign by canonical decimal sign
            if "E" in value or "e" in value:
                self.add2errorlist(
                    _(
                        '[F09]%(linpos)s: Record "%(record)s" field "%(field)s" has non-numerical content: "%(content)s".\n'
                    )
                    % {
                        "linpos": node_instance.linpos(),
                        "record": self.mpathformat(structure_record[MPATH]),
                        "field": field_definition[ID],
                        "content": value,
                    }
                )
            elif field_definition[BFORMAT] == "R":
                lendecimal = len(value.partition(".")[2])
                try:  # convert to float in order to check validity
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
                try:  # convert to float in order to check validity
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
                    try:  # convert to float in order to check validity
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

    def _parse(self, structure_level, inode):
        """ This is the heart of the parsing of incoming messages (but not for xml, json)
            Read the lex_records one by one (self.iternext_lex_record, is an iterator)
            - parse the records.
            - identify record (lookup in structure)
            - identify fields in the record (use the record_definition from the grammar).
            - add grammar-info to records: field-tag,mpath.
            Parameters:
            - structure_level: current grammar/segmentgroup of the grammar-structure.
            - inode: parent node; all parsed records are added as children of inode
            2x recursive: SUBTRANSLATION and segmentgroups
        """
        structure_index = 0  # keep track of where we are in the structure_level
        countnrofoccurences = 0  # number of occurences of current record in structure
        structure_end = len(structure_level)
        # indicate if the next record should be fetched, or if the current_lex_record is still being parsed.
        get_next_lex_record = True
        # it might seem logical to test here 'current_lex_record is None', but
        # this is already used to indicate 'no more records'.
        while True:
            if get_next_lex_record:
                try:
                    current_lex_record = next(self.iternext_lex_record)
                except StopIteration:  # catch when no more lex_record.
                    current_lex_record = None
                get_next_lex_record = False
            if (
                current_lex_record is None
                or structure_level[structure_index][ID] != current_lex_record[ID][VALUE]
            ):
                # is record is required in structure_level, and countnrofoccurences==0: error;
                if structure_level[structure_index][MIN] and not countnrofoccurences:
                    # enough check here; message is
                    # validated more accurate later
                    try:
                        raise InMessageError(
                            self.messagetypetxt
                            + _(
                                '[S50]: Line:%(line)s pos:%(pos)s record:"%(record)s": message has an error in its structure; this record is not allowed here. Scanned in message definition until mandatory record: "%(looked)s".'
                            ),
                            {
                                "record": current_lex_record[ID][VALUE],
                                "line": current_lex_record[ID][LIN],
                                "pos": current_lex_record[ID][POS],
                                "looked": self.mpathformat(
                                    structure_level[structure_index][MPATH]
                                ),
                            },
                        )
                    except TypeError:  # when no UNZ (edifact)
                        raise InMessageError(
                            self.messagetypetxt
                            + _('[S51]: Missing mandatory record "%(record)s".'),
                            {
                                "record": self.mpathformat(
                                    structure_level[structure_index][MPATH]
                                )
                            },
                        )
                structure_index += 1
                if (
                    structure_index == structure_end
                ):  # current_lex_record is not in this level. Go level up
                    # if on 'first level': give specific error
                    if (
                        current_lex_record is not None
                        and structure_level == self.defmessage.structure
                    ):
                        raise InMessageError(
                            self.messagetypetxt
                            + _(
                                '[S50]: Line:%(line)s pos:%(pos)s record:"%(record)s": message has an error in its structure; this record is not allowed here. Scanned in message definition until mandatory record: "%(looked)s".'
                            ),
                            {
                                "record": current_lex_record[ID][VALUE],
                                "line": current_lex_record[ID][LIN],
                                "pos": current_lex_record[ID][POS],
                                "looked": self.mpathformat(
                                    structure_level[structure_index - 1][MPATH]
                                ),
                            },
                        )
                    # return either None (no more lex_records to parse) or the last
                    # current_lex_record (the last current_lex_record is not found in this
                    # level)
                    return current_lex_record
                countnrofoccurences = 0
                continue  # continue while-loop: get_next_lex_record is false as no match with structure is made; go and look at next record of structure
            # record is found in grammar
            countnrofoccurences += 1
            newnode = node.Node(
                record=self._parsefields(
                    current_lex_record, structure_level[structure_index]
                ),
                linpos_info=(current_lex_record[0][LIN], current_lex_record[0][POS]),
            )  # make new node
            inode.append(
                newnode
            )  # succes! append new node as a child to current (parent)node
            if SUBTRANSLATION in structure_level[structure_index]:
                # start a SUBTRANSLATION; find the right messagetype, etc
                messagetype = newnode.enhancedget(
                    structure_level[structure_index][SUBTRANSLATION]
                )
                if not messagetype:
                    raise TranslationNotFoundError(
                        _('Could not find SUBTRANSLATION "%(sub)s" in (sub)message.'),
                        {"sub": structure_level[structure_index][SUBTRANSLATION]},
                    )
                messagetype = self._manipulatemessagetype(messagetype, inode)
                try:
                    defmessage = grammar.grammarread(
                        self.__class__.__name__,
                        messagetype,
                        typeofgrammarfile="grammars",
                    )
                except BotsImportError:
                    raisenovalidmapping_error = True
                    if hasattr(self.defmessage.module, "getmessagetype"):
                        messagetype2 = runscript(
                            self.defmessage.module,
                            self.defmessage.grammarname,
                            "getmessagetype",
                            editype=self.__class__.__name__,
                            messagetype=messagetype,
                        )
                        if messagetype2:
                            try:
                                defmessage = grammar.grammarread(
                                    self.__class__.__name__,
                                    messagetype2,
                                    typeofgrammarfile="grammars",
                                )
                                raisenovalidmapping_error = False
                            except BotsImportError:
                                pass
                    if raisenovalidmapping_error:
                        raise TranslationNotFoundError(
                            _(
                                'No (valid) grammar for editype "%(editype)s" messagetype "%(messagetype)s".'
                            ),
                            {
                                "editype": self.__class__.__name__,
                                "messagetype": messagetype,
                            },
                        )
                self.messagecount += 1
                self.messagetypetxt = _(
                    "Message nr %(count)s, type %(type)s, "
                    % {"count": self.messagecount, "type": messagetype}
                )
                current_lex_record = self._parse(
                    structure_level=defmessage.structure[0][LEVEL], inode=newnode
                )
                # copy messagetype into 1st segment of subtranslation (eg UNH, ST)
                newnode.queries = {"messagetype": messagetype}
                newnode.queries.update(defmessage.syntax)
                # ~ newnode.queries = defmessage.syntax.copy()       #if using this line instead of previous 2: gives errors eg in incoming edifact...do not understand why
                self.checkmessage(
                    newnode, defmessage, subtranslation=True
                )  # check the results of the subtranslation
                # ~ end SUBTRANSLATION
                self.messagetypetxt = ""
                # get_next_lex_record is still False; we are trying to match the last (not
                # matched) record from the SUBTRANSLATION (named 'current_lex_record').
            else:
                if (
                    LEVEL in structure_level[structure_index]
                ):  # if header, go parse segmentgroup (recursive)
                    current_lex_record = self._parse(
                        structure_level=structure_level[structure_index][LEVEL],
                        inode=newnode,
                    )
                    # get_next_lex_record is still False; the current_lex_record that was not
                    # matched in lower segmentgroups is still being parsed.
                else:
                    get_next_lex_record = True
                # accomodate for UNS = UNS construction
                if (
                    structure_level[structure_index][MIN]
                    == structure_level[structure_index][MAX]
                    == countnrofoccurences
                ):
                    if structure_index + 1 == structure_end:
                        pass
                    else:
                        structure_index += 1
                        countnrofoccurences = 0

    @staticmethod
    def _manipulatemessagetype(messagetype, inode):
        """ default: just return messagetype. """
        return messagetype

    def _readcontent_edifile(self):
        """ read content of edi file to memory.
        """
        logger.debug('Read edi file "%(filename)s".', self.ta_info)
        self.rawinput = readdata(
            filename=self.ta_info["filename"],
            charset=self.ta_info["charset"],
            errors=self.ta_info["checkcharsetin"],
        )

    def _sniff(self):
        """ sniffing: hard coded parsing of edi file.
            method is specified in subclasses.
        """
        pass

    def checkenvelope(self):
        pass

    def nextmessage(self):
        """ Passes each 'message' to the mapping script.
        """
        # node preprocessing via user exit indicated in syntax
        preprocess_nodes = self.ta_info.get("preprocess_nodes", False)
        if callable(preprocess_nodes):
            preprocess_nodes(thisnode=self)
        if (
            self.defmessage.nextmessage is not None
        ):  # if nextmessage defined in grammar: split up messages
            # first: count number of messages
            self.ta_info["total_number_of_messages"] = self.getcountoccurrences(
                *self.defmessage.nextmessage
            )
            # yield the messages, using nextmessage
            count = 0
            self.root.processqueries({}, len(self.defmessage.nextmessage))
            # eachmessage is a list: [mpath,mpath, etc, node]
            for eachmessage in self.getloop_including_mpath(
                *self.defmessage.nextmessage
            ):
                count += 1
                ta_info = self.ta_info.copy()
                ta_info.update(eachmessage[-1].queries)
                ta_info["message_number"] = count
                ta_info[
                    "bots_accessenvelope"
                ] = self.root  # give mappingscript access to envelope
                yield self._initmessagefromnode(
                    eachmessage[-1], ta_info, eachmessage[:-1]
                )
            if (
                self.defmessage.nextmessage2 is not None
            ):  # edifact uses nextmessage2 for UNB-UNG
                # first: count number of messages
                self.ta_info["total_number_of_messages"] = self.getcountoccurrences(
                    *self.defmessage.nextmessage2
                )
                # yield the messages, using nextmessage2
                self.root.processqueries({}, len(self.defmessage.nextmessage2))
                count = 0
                # eachmessage is a list: [mpath,mpath, etc, node]
                for eachmessage in self.getloop_including_mpath(
                    *self.defmessage.nextmessage2
                ):
                    count += 1
                    ta_info = self.ta_info.copy()
                    ta_info.update(eachmessage.queries[-1])
                    ta_info["message_number"] = count
                    ta_info[
                        "bots_accessenvelope"
                    ] = self.root  # give mappingscript access to envelope
                    yield self._initmessagefromnode(
                        eachmessage[-1], ta_info, eachmessage[:-1]
                    )
        # for csv/fixed: nextmessageblock indicates which field(s) determines a message
        elif self.defmessage.nextmessageblock is not None:
            # --> as long as the field(s) has same value, it is the same message
            # note there is only one recordtype (as checked in grammar.py)
            # first: count number of messages
            count = 0
            for line in self.root.children:
                kriterium = line.enhancedget(self.defmessage.nextmessageblock)
                if not count:
                    count += 1
                    oldkriterium = kriterium
                elif kriterium != oldkriterium:
                    count += 1
                    oldkriterium = kriterium
                # ~ else:
                # ~ pass    #if kriterium is the same
            self.ta_info["total_number_of_messages"] = count
            # yield the messages, using nextmessageblock
            count = 0
            for line in self.root.children:
                kriterium = line.enhancedget(self.defmessage.nextmessageblock)
                if not count:
                    count += 1
                    oldkriterium = kriterium
                    newroot = node.Node()  # make new empty root node.
                elif kriterium != oldkriterium:
                    count += 1
                    oldkriterium = kriterium
                    ta_info = self.ta_info.copy()
                    ta_info.update(
                        oldline.queries
                    )  # update ta_info with information (from previous line) 20100905
                    ta_info["message_number"] = count
                    yield self._initmessagefromnode(newroot, ta_info)
                    newroot = node.Node()  # make new empty root node.
                else:
                    pass  # if kriterium is the same
                newroot.append(line)
                oldline = line  # save line 20100905
            else:
                if count:  # not if count is zero (that is, if there are no lines)
                    ta_info = self.ta_info.copy()
                    ta_info.update(
                        line.queries
                    )  # update ta_info with information (from last line) 20100904
                    ta_info["message_number"] = count
                    yield self._initmessagefromnode(newroot, ta_info)
        else:  # no split up is indicated in grammar. Normally you really would...
            # if contains root-record or explicitly indicated (csv): pass whole tree
            if self.root.record or self.ta_info.get("pass_all", False):
                ta_info = self.ta_info.copy()
                ta_info.update(self.root.queries)
                ta_info["total_number_of_messages"] = 1
                ta_info["message_number"] = 1
                ta_info[
                    "bots_accessenvelope"
                ] = self.root  # give mappingscript access to envelop
                yield self._initmessagefromnode(self.root, ta_info)
            else:  # pass nodes under root one by one
                # first: count number of messages
                total_number_of_messages = len(self.root.children)
                # yield the messages
                count = 0
                for child in self.root.children:
                    count += 1
                    ta_info = self.ta_info.copy()
                    ta_info.update(child.queries)
                    ta_info["total_number_of_messages"] = total_number_of_messages
                    ta_info["message_number"] = count
                    ta_info[
                        "bots_accessenvelope"
                    ] = self.root  # give mappingscript access to envelope
                    yield self._initmessagefromnode(child, ta_info)

    @classmethod
    def _initmessagefromnode(cls, inode, ta_info, envelope=None):
        """ initialize a inmessage-object from node in tree.
            used in nextmessage.
        """
        messagefromnode = cls(ta_info)
        messagefromnode.root = inode
        messagefromnode.envelope = envelope
        return messagefromnode

    def _canonicaltree(self, node_instance, structure):
        """ For nodes: check min and max occurence; sort the records conform grammar
        """
        super(InMessage, self)._canonicaltree(node_instance, structure)
        if QUERIES in structure:
            node_instance.get_queries_from_edi(structure)
