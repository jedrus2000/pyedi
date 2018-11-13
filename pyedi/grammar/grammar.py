from gettext import gettext as _

from pyedi.botslib.consts import *
from pyedi.botslib import (
    GrammarError,
    GrammarPartMissing,
    botsimport,
)


# used in this module to indicate part of grammar is already read and/or has errors

ERROR_IN_GRAMMAR = "BOTS_error_1$%3@7#!%+_)_+[{]}"
# no record should be called like this ;-))


class Grammar(object):
    """ Class for translation grammar. A grammar contains the description of an edi-file; this is used in reading or writing an edi file.
        The grammar is read from a grammar file; a python python.
        A grammar file has several grammar parts , eg 'structure' and 'recorddefs'.
        Grammar parts are either in the grammar file  itself or a imported from another grammar-file.

        in a grammar 'structure' is a list of dicts describing the sequence and relationships between the record(group)s:
            attributes of each record(group) in structure:
            -   ID       record id
            -   MIN      min #occurences record or group
            -   MAX      max #occurences record of group
            -   LEVEL    child-records
            added after reading the grammar (so: not in grammar-file):
            -   MPATH    mpath of record
            -   FIELDS   (added from recordsdefs via lookup)
        in a grammar 'recorddefs' describes the (sub) fields for the records:
        -   'recorddefs' is a dict where key is the recordID, value is list of (sub) fields
            each (sub)field is a tuple of (field or subfield)
            field is tuple of (ID, MANDATORY, LENGTH, FORMAT)
            subfield is tuple of (ID, MANDATORY, tuple of fields)

        every grammar-file is read once (default python import-machinery).
        The information in a grammar is checked and manipulated by bots.
        if a structure or recorddef has already been read, Bots skips most of the checks.
    """

    def __init__(self, typeofgrammarfile, editype, grammarname):
        """ import grammar; read syntax"""
        self.module, self.grammarname = botsimport(
            typeofgrammarfile, editype, grammarname
        )
        # get syntax from grammar file
        self.original_syntaxfromgrammar = getattr(self.module, "syntax", {})
        if not isinstance(self.original_syntaxfromgrammar, dict):
            raise GrammarError(
                _('Grammar "%(grammar)s": syntax is not a dict{}.'),
                {"grammar": self.grammarname},
            )

    def _init_restofgrammar(self):
        self.nextmessage = getattr(self.module, "nextmessage", None)
        self.nextmessage2 = getattr(self.module, "nextmessage2", None)
        self.nextmessageblock = getattr(self.module, "nextmessageblock", None)
        # checks on nextmessage, nextmessage2, nextmessageblock
        if self.nextmessage is None:
            if self.nextmessage2 is not None:
                raise GrammarError(
                    _(
                        'Grammar "%(grammar)s": if nextmessage2: nextmessage has to be used.'
                    ),
                    {"grammar": self.grammarname},
                )
        else:
            if self.nextmessageblock is not None:
                raise GrammarError(
                    _(
                        'Grammar "%(grammar)s": nextmessageblock and nextmessage not both allowed.'
                    ),
                    {"grammar": self.grammarname},
                )

        if self.syntax[
            "has_structure"
        ]:  # most grammars have a structure; but eg templatehtml not (only syntax)
            # read recorddefs.
            # recorddefs are checked and changed, so need to indicate if recordsdef has already been checked and changed.
            # done by setting entry 'BOTS_1$@#%_error' in recorddefs; if this entry is
            # True: read, errors; False: read OK.
            try:
                self._dorecorddefs()
            except GrammarPartMissing:  # basic checks on recordsdef - it is not there, or not a dict, etc.
                raise
            except:
                self.recorddefs[
                    ERROR_IN_GRAMMAR
                ] = True  # mark recorddefs as 'already read - with errors'
                raise
            else:
                self.recorddefs[
                    ERROR_IN_GRAMMAR
                ] = False  # mark recorddefs as 'read and checked OK'
            # read structure
            # structure is checked and changed, so need to indicate if structure has already been checked and changed.
            # done by setting entry 'BOTS_1$@#%_error' in structure[0]; if this entry
            # is True: read, errors; False: read OK.
            try:
                self._dostructure()
            except GrammarPartMissing:  # basic checks on strucure - it is not there, or not a list, etc.
                raise
            except:
                self.structure[0][
                    ERROR_IN_GRAMMAR
                ] = True  # mark structure as 'already read - with errors'
                raise
            else:
                self.structure[0][
                    ERROR_IN_GRAMMAR
                ] = False  # mark structure as 'read and checked OK'
            # link recordsdefs to structure
            # as structure can be re-used/imported from other grammars, do this always when reading grammar.
            self._linkrecorddefs2structure(self.structure)
        self.class_specific_tests()

    def _dorecorddefs(self):
        """ 1. check the recorddefinitions for validity.
            2. adapt in field-records: normalise length lists, set bool ISFIELD, etc
        """
        try:
            self.recorddefs = getattr(self.module, "recorddefs")
        except AttributeError:
            _exception = GrammarPartMissing(
                _('Grammar "%(grammar)s": no recorddefs, is required.'),
                {"grammar": self.grammarname},
            )
            _exception.__cause__ = None
            raise _exception
        if not isinstance(self.recorddefs, dict):
            raise GrammarPartMissing(
                _('Grammar "%(grammar)s": recorddefs is not a dict.'),
                {"grammar": self.grammarname},
            )

        if (
            ERROR_IN_GRAMMAR in self.recorddefs
        ):  # recorddefs is checked already (in this run).
            if self.recorddefs[
                ERROR_IN_GRAMMAR
            ]:  # already did checks - and an error was found.
                raise GrammarError(
                    _(
                        'Grammar "%(grammar)s": recorddefs has error that is already reported in this run.'
                    ),
                    {"grammar": self.grammarname},
                )
            return  # already did checks - result OK! skip checks
        # not checked (in this run): so check the recorddefs
        for recordid, fields in self.recorddefs.items():
            if not isinstance(recordid, str):
                raise GrammarError(
                    _(
                        'Grammar "%(grammar)s", in recorddefs, record "%(record)s": is not a string.'
                    ),
                    {"grammar": self.grammarname, "record": recordid},
                )
            if not recordid:
                raise GrammarError(
                    _(
                        'Grammar "%(grammar)s", in recorddefs, record "%(record)s": recordid with empty string.'
                    ),
                    {"grammar": self.grammarname, "record": recordid},
                )
            if not isinstance(fields, list):
                raise GrammarError(
                    _(
                        'Grammar "%(grammar)s", in recorddefs, record "%(record)s": no correct fields found.'
                    ),
                    {"grammar": self.grammarname, "record": recordid},
                )
            if self.__class__.__name__ in ['Xml', 'Json']:
                if len(fields) < 1:
                    raise GrammarError(
                        _(
                            'Grammar "%(grammar)s", in recorddefs, record "%(record)s": too few fields.'
                        ),
                        {"grammar": self.grammarname, "record": recordid},
                    )
            else:
                if len(fields) < 2:
                    raise GrammarError(
                        _(
                            'Grammar "%(grammar)s", in recorddefs, record "%(record)s": too few fields.'
                        ),
                        {"grammar": self.grammarname, "record": recordid},
                    )

            has_botsid = False  # to check if BOTSID is present
            fieldnamelist = []  # to check for double fieldnames
            for field in fields:
                self._checkfield(field, recordid)
                if not field[ISFIELD]:  # if composite
                    for sfield in field[SUBFIELDS]:
                        self._checkfield(sfield, recordid)
                        if sfield[ID] in fieldnamelist:
                            raise GrammarError(
                                _(
                                    'Grammar "%(grammar)s", in recorddefs, record "%(record)s": field "%(field)s" appears twice. Field names should be unique within a record.'
                                ),
                                {
                                    "grammar": self.grammarname,
                                    "record": recordid,
                                    "field": sfield[ID],
                                },
                            )
                        fieldnamelist.append(sfield[ID])
                else:
                    if field[ID] == "BOTSID":
                        has_botsid = True
                    if field[ID] in fieldnamelist:
                        raise GrammarError(
                            _(
                                'Grammar "%(grammar)s", in recorddefs, record "%(record)s": field "%(field)s" appears twice. Field names should be unique within a record.'
                            ),
                            {
                                "grammar": self.grammarname,
                                "record": recordid,
                                "field": field[ID],
                            },
                        )
                    fieldnamelist.append(field[ID])

            if not has_botsid:  # there is no field 'BOTSID' in record
                raise GrammarError(
                    _(
                        'Grammar "%(grammar)s", in recorddefs, record "%(record)s": no field BOTSID.'
                    ),
                    {"grammar": self.grammarname, "record": recordid},
                )

    def _checkfield(self, field, recordid):
        #'normalise' field: make list equal length
        len_field = len(field)
        if len_field == 3:  # that is: composite
            field += [None, False, None, None, "A", 1]
        elif len_field == 4:  # that is: field (not a composite)
            field += [True, 0, 0, "A", 1]
        # each field is now equal length list
        # ~ elif len_field == 9:               # this happens when there are errors in a table and table is read again --> should not be possible
        # ~ raise GrammarError(_('Grammar "%(grammar)s": error in grammar; error is already reported in this run.'),
        # ~ {'grammar':self.grammarname})
        else:
            raise GrammarError(
                _(
                    'Grammar "%(grammar)s", in recorddefs, record "%(record)s", field "%(field)s": list has invalid number of arguments.'
                ),
                {"grammar": self.grammarname, "record": recordid, "field": field[ID]},
            )
        if not isinstance(field[ID], str) or not field[ID]:
            raise GrammarError(
                _(
                    'Grammar "%(grammar)s", in recorddefs, record "%(record)s", field "%(field)s": fieldID has to be a string.'
                ),
                {"grammar": self.grammarname, "record": recordid, "field": field[ID]},
            )
        if isinstance(field[MANDATORY], str):
            if field[MANDATORY] not in "MC":
                raise GrammarError(
                    _(
                        'Grammar "%(grammar)s", in recorddefs, record "%(record)s", field "%(field)s": mandatory/conditional must be "M" or "C".'
                    ),
                    {
                        "grammar": self.grammarname,
                        "record": recordid,
                        "field": field[ID],
                    },
                )
            field[MANDATORY] = 0 if field[MANDATORY] == "C" else 1
        elif isinstance(field[MANDATORY], tuple):
            if not isinstance(field[MANDATORY][0], str):
                raise GrammarError(
                    _(
                        'Grammar "%(grammar)s", in recorddefs, record "%(record)s", field "%(field)s": mandatory/conditional must be "M" or "C".'
                    ),
                    {
                        "grammar": self.grammarname,
                        "record": recordid,
                        "field": field[ID],
                    },
                )
            if field[MANDATORY][0] not in "MC":
                raise GrammarError(
                    _(
                        'Grammar "%(grammar)s", in recorddefs, record "%(record)s", field "%(field)s": mandatory/conditional must be "M" or "C".'
                    ),
                    {
                        "grammar": self.grammarname,
                        "record": recordid,
                        "field": field[ID],
                    },
                )
            if not isinstance(field[MANDATORY][1], int):
                raise GrammarError(
                    _(
                        'Grammar "%(grammar)s", in recorddefs, record "%(record)s", field "%(field)s": number of repeats must be integer.'
                    ),
                    {
                        "grammar": self.grammarname,
                        "record": recordid,
                        "field": field[ID],
                    },
                )
            field[MAXREPEAT] = field[MANDATORY][1]
            field[MANDATORY] = 0 if field[MANDATORY][0] == "C" else 1
        else:
            raise GrammarError(
                _(
                    'Grammar "%(grammar)s", in recorddefs, record "%(record)s", field "%(field)s": mandatory/conditional has to be a string (or tuple in case of repeating field).'
                ),
                {"grammar": self.grammarname, "record": recordid, "field": field[ID]},
            )
        if field[ISFIELD]:  # that is: field, and not a composite
            # get MINLENGTH (from tuple or if fixed
            if isinstance(field[LENGTH], (int, float)):
                if self.__class__.__name__ == 'Fixed':
                    field[MINLENGTH] = field[LENGTH]
            elif isinstance(field[LENGTH], tuple):
                if not isinstance(field[LENGTH][0], (int, float)):
                    raise GrammarError(
                        _(
                            'Grammar "%(grammar)s", in recorddefs, record "%(record)s", field "%(field)s": min length "%(min)s" has to be a number.'
                        ),
                        {
                            "grammar": self.grammarname,
                            "record": recordid,
                            "field": field[ID],
                            "min": field[LENGTH][0],
                        },
                    )
                if not isinstance(field[LENGTH][1], (int, float)):
                    raise GrammarError(
                        _(
                            'Grammar "%(grammar)s", in recorddefs, record "%(record)s", field "%(field)s": max length "%(max)s" has to be a number.'
                        ),
                        {
                            "grammar": self.grammarname,
                            "record": recordid,
                            "field": field[ID],
                            "max": field[LENGTH][1],
                        },
                    )
                if field[LENGTH][0] > field[LENGTH][1]:
                    raise GrammarError(
                        _(
                            'Grammar "%(grammar)s", in recorddefs, record "%(record)s", field "%(field)s": min length "%(min)s" must be > max length "%(max)s".'
                        ),
                        {
                            "grammar": self.grammarname,
                            "record": recordid,
                            "field": field[ID],
                            "min": field[LENGTH][0],
                            "max": field[LENGTH][1],
                        },
                    )
                field[MINLENGTH] = field[LENGTH][0]
                field[LENGTH] = field[LENGTH][1]
            else:
                raise GrammarError(
                    _(
                        'Grammar "%(grammar)s", in recorddefs, record "%(record)s", field "%(field)s": length "%(len)s" has to be number or (min,max).'
                    ),
                    {
                        "grammar": self.grammarname,
                        "record": recordid,
                        "field": field[ID],
                        "len": field[LENGTH],
                    },
                )
            if field[LENGTH] < 1:
                raise GrammarError(
                    _(
                        'Grammar "%(grammar)s", in recorddefs, record "%(record)s", field "%(field)s": length "%(len)s" has to be at least 1.'
                    ),
                    {
                        "grammar": self.grammarname,
                        "record": recordid,
                        "field": field[ID],
                        "len": field[LENGTH],
                    },
                )
            if field[MINLENGTH] < 0:
                raise GrammarError(
                    _(
                        'Grammar "%(grammar)s", in recorddefs, record "%(record)s", field "%(field)s": minlength "%(len)s" has to be at least 0.'
                    ),
                    {
                        "grammar": self.grammarname,
                        "record": recordid,
                        "field": field[ID],
                        "len": field[LENGTH],
                    },
                )
            # format
            if not isinstance(field[FORMAT], str):
                raise GrammarError(
                    _(
                        'Grammar "%(grammar)s", in recorddefs, record "%(record)s", field "%(field)s": format "%(format)s" has to be a string.'
                    ),
                    {
                        "grammar": self.grammarname,
                        "record": recordid,
                        "field": field[ID],
                        "format": field[FORMAT],
                    },
                )
            self._manipulatefieldformat(field, recordid)
            if field[BFORMAT] in "NIR":
                if isinstance(field[LENGTH], float):
                    # Does not work for more than 9 decimal places.
                    field[DECIMALS] = int((field[LENGTH] % 1) * 10.0001)
                    field[LENGTH] = int(field[LENGTH])
                    if field[DECIMALS] >= field[LENGTH]:
                        raise GrammarError(
                            _(
                                'Grammar "%(grammar)s", in recorddefs, record "%(record)s", field "%(field)s": field length "%(len)s" has to be greater that nr of decimals "%(decimals)s".'
                            ),
                            {
                                "grammar": self.grammarname,
                                "record": recordid,
                                "field": field[ID],
                                "decimals": field[DECIMALS],
                            },
                        )
                if isinstance(field[MINLENGTH], float):
                    field[MINLENGTH] = int(field[MINLENGTH])
            else:  # if format 'R', A, D, T
                if isinstance(field[LENGTH], float):
                    raise GrammarError(
                        _(
                            'Grammar "%(grammar)s", in recorddefs, record "%(record)s", field "%(field)s": if format "%(format)s", no length "%(len)s".'
                        ),
                        {
                            "grammar": self.grammarname,
                            "record": recordid,
                            "field": field[ID],
                            "format": field[FORMAT],
                            "len": field[LENGTH],
                        },
                    )
                if isinstance(field[MINLENGTH], float):
                    raise GrammarError(
                        _(
                            'Grammar "%(grammar)s", in recorddefs, record "%(record)s", field "%(field)s": if format "%(format)s", no minlength "%(len)s".'
                        ),
                        {
                            "grammar": self.grammarname,
                            "record": recordid,
                            "field": field[ID],
                            "format": field[FORMAT],
                            "len": field[MINLENGTH],
                        },
                    )
        else:  # check composite
            if not isinstance(field[SUBFIELDS], list):
                raise GrammarError(
                    _(
                        'Grammar "%(grammar)s", in recorddefs, record "%(record)s", field "%(field)s": is a composite field, has to have subfields.'
                    ),
                    {
                        "grammar": self.grammarname,
                        "record": recordid,
                        "field": field[ID],
                    },
                )
            if len(field[SUBFIELDS]) < 2:
                raise GrammarError(
                    _(
                        'Grammar "%(grammar)s", in recorddefs, record "%(record)s", field "%(field)s" has < 2 sfields.'
                    ),
                    {
                        "grammar": self.grammarname,
                        "record": recordid,
                        "field": field[ID],
                    },
                )

    def _dostructure(self):
        """ 1. check the structure for validity.
            2. adapt in structure: Add keys: mpath, count
            3. remember that structure is checked and adapted (so when grammar is read again, no checking/adapt needed)
        """
        try:
            self.structure = getattr(self.module, "structure")
        except AttributeError:
            _exception = GrammarPartMissing(
                _('Grammar "%(grammar)s": no structure, is required.'),
                {"grammar": self.grammarname},
            )
            _exception.__cause__ = None
            raise _exception
        if not isinstance(self.structure, list):
            raise GrammarPartMissing(
                _('Grammar "%(grammar)s": structure is not a list.'),
                {"grammar": self.grammarname},
            )
        if len(self.structure) != 1:
            raise GrammarPartMissing(
                _(
                    'Grammar "%(grammar)s", in structure: structure must have exactlty one root record.'
                ),
                {"grammar": self.grammarname},
            )
        if not isinstance(self.structure[0], dict):
            raise GrammarPartMissing(
                _(
                    'Grammar "%(grammar)s": in structure: expect a dict for root record, but did not find that.'
                ),
                {"grammar": self.grammarname},
            )

        if (
            ERROR_IN_GRAMMAR in self.structure[0]
        ):  # structure is checked already (in this run).
            if self.structure[0][
                ERROR_IN_GRAMMAR
            ]:  # already did checks - and an error was found.
                raise GrammarError(
                    _(
                        'Grammar "%(grammar)s": structure has error that is already reported in this run.'
                    ),
                    {"grammar": self.grammarname},
                )
            return  # already did checks - result OK! skip checks
        # not checked (in this run): so check the structure
        self._checkstructure(self.structure, [])
        if self.syntax["checkcollision"]:
            self._checkbackcollision(self.structure)
            self._checknestedcollision(self.structure)
        self._checkbotscollision(self.structure)

    def _checkstructure(self, structure, mpath):
        """ Recursive
            1.   Check structure.
            2.   Add keys: mpath, count
        """
        if not isinstance(structure, list):
            raise GrammarError(
                _('Grammar "%(grammar)s", in structure, at "%(mpath)s": not a list.'),
                {"grammar": self.grammarname, "mpath": mpath},
            )
        for i in structure:
            if not isinstance(i, dict):
                raise GrammarError(
                    _(
                        'Grammar "%(grammar)s", in structure, at "%(mpath)s": record should be a dict: "%(record)s".'
                    ),
                    {"grammar": self.grammarname, "mpath": mpath, "record": i},
                )
            if ID not in i:
                raise GrammarError(
                    _(
                        'Grammar "%(grammar)s", in structure, at "%(mpath)s": record without ID: "%(record)s".'
                    ),
                    {"grammar": self.grammarname, "mpath": mpath, "record": i},
                )
            if not isinstance(i[ID], str):
                raise GrammarError(
                    _(
                        'Grammar "%(grammar)s", in structure, at "%(mpath)s": recordid of record is not a string: "%(record)s".'
                    ),
                    {"grammar": self.grammarname, "mpath": mpath, "record": i},
                )
            if not i[ID]:
                raise GrammarError(
                    _(
                        'Grammar "%(grammar)s", in structure, at "%(mpath)s": recordid of record is empty: "%(record)s".'
                    ),
                    {"grammar": self.grammarname, "mpath": mpath, "record": i},
                )
            if MIN not in i:
                raise GrammarError(
                    _(
                        'Grammar "%(grammar)s", in structure, at "%(mpath)s": record without MIN: "%(record)s".'
                    ),
                    {"grammar": self.grammarname, "mpath": mpath, "record": i},
                )
            if MAX not in i:
                raise GrammarError(
                    _(
                        'Grammar "%(grammar)s", in structure, at "%(mpath)s": record without MAX: "%(record)s".'
                    ),
                    {"grammar": self.grammarname, "mpath": mpath, "record": i},
                )
            if not isinstance(i[MIN], int):
                raise GrammarError(
                    _(
                        'Grammar "%(grammar)s", in structure, at "%(mpath)s": record where MIN is not whole number: "%(record)s".'
                    ),
                    {"grammar": self.grammarname, "mpath": mpath, "record": i},
                )
            if not isinstance(i[MAX], int):
                raise GrammarError(
                    _(
                        'Grammar "%(grammar)s", in structure, at "%(mpath)s": record where MAX is not whole number: "%(record)s".'
                    ),
                    {"grammar": self.grammarname, "mpath": mpath, "record": i},
                )
            if not i[MAX]:
                raise GrammarError(
                    _(
                        'Grammar "%(grammar)s", in structure, at "%(mpath)s": MAX is zero: "%(record)s".'
                    ),
                    {"grammar": self.grammarname, "mpath": mpath, "record": i},
                )
            if i[MIN] > i[MAX]:
                raise GrammarError(
                    _(
                        'Grammar "%(grammar)s", in structure, at "%(mpath)s": record where MIN > MAX: "%(record)s".'
                    ),
                    {
                        "grammar": self.grammarname,
                        "mpath": mpath,
                        "record": str(i)[:100],
                    },
                )
            i[MPATH] = mpath + [i[ID]]
            if LEVEL in i:
                self._checkstructure(i[LEVEL], i[MPATH])

    def _checkbackcollision(self, structure, collision=None):
        """ Recursive.
            Check if grammar has back-collision problem. A message with collision problems is ambiguous.
            Case 1:  AAA BBB AAA
            Case 2:  AAA     BBB
                     BBB CCC
        """
        if not collision:
            collision = []
        headerissave = False
        for i in structure:
            if i[ID] in collision:
                raise GrammarError(
                    _(
                        'Grammar "%(grammar)s", in structure: back-collision detected at record "%(mpath)s".'
                    ),
                    {"grammar": self.grammarname, "mpath": i[MPATH]},
                )
            if i[MIN]:
                headerissave = True
                if (
                    i[MIN] == i[MAX]
                ):  # so: fixed number of occurences; can not lead to collision as  is always clear where in structure record is
                    collision = []  # NOTE: this is mainly used for MIN=1, MAX=1
                else:
                    collision = [i[ID]]  # previous records do not cause collision.
            else:
                collision.append(i[ID])
            if LEVEL in i:
                if i[MIN] == i[MAX] == 1:
                    returncollision, returnheaderissave = self._checkbackcollision(
                        i[LEVEL]
                    )
                else:
                    returncollision, returnheaderissave = self._checkbackcollision(
                        i[LEVEL], [i[ID]]
                    )
                collision.extend(returncollision)
                # if one of segment(groups) is required, there is always a segment after
                # the header segment; so remove header from nowcollision:
                if returnheaderissave and i[ID] in collision:
                    collision.remove(i[ID])
        return (
            collision,
            headerissave,
        )  # collision is used to update on higher level; cleared indicates the header segment can not collide anymore

    def _checkbotscollision(self, structure):
        """ Recursive.
            Within one level: if twice the same tag: use BOTSIDNR.
        """
        collision = {}
        for i in structure:
            if i[ID] in collision:
                i[BOTSIDNR] = str(collision[i[ID]] + 1)
                collision[i[ID]] = collision[i[ID]] + 1
            else:
                i[BOTSIDNR] = "1"
                collision[i[ID]] = 1
            if LEVEL in i:
                self._checkbotscollision(i[LEVEL])
        return

    def _checknestedcollision(self, structure, collision=None):
        """ Recursive.
            Check if grammar has nested-collision problem. A message with collision problems is ambiguous.
            Case 1: AAA
                    BBB CCC
                        AAA
        """
        if not collision:
            levelcollision = []
        else:
            levelcollision = collision[:]
        for i in reversed(structure):
            if LEVEL in i:
                if i[MIN] == i[MAX] == 1:
                    isa_safeheadersegment = self._checknestedcollision(
                        i[LEVEL], levelcollision
                    )
                else:
                    isa_safeheadersegment = self._checknestedcollision(
                        i[LEVEL], levelcollision + [i[ID]]
                    )
            else:
                isa_safeheadersegment = False
            # fixed number of occurences. this can be handled umambigiously: no check needed
            if isa_safeheadersegment or i[MIN] == i[MAX]:
                pass  # no check needed
            elif i[ID] in levelcollision:
                raise GrammarError(
                    _(
                        'Grammar "%(grammar)s", in structure: nesting collision detected at record "%(mpath)s".'
                    ),
                    {"grammar": self.grammarname, "mpath": i[MPATH]},
                )
            if i[MIN]:
                levelcollision = []  # empty uppercollision
        return not bool(levelcollision)

    def _linkrecorddefs2structure(self, structure):
        """ recursive
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
            if LEVEL in i:
                self._linkrecorddefs2structure(i[LEVEL])

    def class_specific_tests(self):
        """ default function, subclasses have the actual checks."""
        pass

    def display(self, structure, level=0):
        """ Draw grammar, with indentation for levels.
            For debugging.
        """
        for i in structure:
            print("Record: ", i[MPATH], i)
            for field in i[FIELDS]:
                print("    Field: ", field)
            if LEVEL in i:
                self.display(i[LEVEL], level + 1)

    # bots interpreters the format from the grammer; left side are the allowed values; right side are the internal formats bots uses.
    # the list directly below are the default values for the formats, subclasses can have their own list.
    # this makes it possible to use x12-formats for x12, edifact-formats for edifact etc
    formatconvert = {
        "A": "A",  # alfanumerical
        "AN": "A",  # alfanumerical
        # ~ 'AR':'A',       #right aligned alfanumerical field, used in fixed records.
        "D": "D",  # date
        "DT": "D",  # date-time
        "T": "T",  # time
        "TM": "T",  # time
        "N": "N",  # numerical, fixed decimal. Fixed nr of decimals; if no decimal used: whole number, integer
        # ~ 'NL':'N',       #numerical, fixed decimal. In fixed format: no preceding zeros, left aligned,
        # ~ 'NR':'N',       #numerical, fixed decimal. In fixed format: preceding blancs, right aligned,
        "R": "R",  # numerical, any number of decimals; the decimal point is 'floating'
        # ~ 'RL':'R',       #numerical, any number of decimals. fixed: no preceding zeros, left aligned
        # ~ 'RR':'R',       #numerical, any number of decimals. fixed: preceding blancs, right aligned
        "I": "I",  # numercial, implicit decimal
    }

    def _manipulatefieldformat(self, field, recordid):
        try:
            field[BFORMAT] = self.formatconvert[field[FORMAT]]
        except KeyError:
            raise GrammarError(
                _(
                    'Grammar "%(grammar)s", record "%(record)s", field "%(field)s": format "%(format)s" has to be one of "%(keys)s".'
                ),
                {
                    "grammar": self.grammarname,
                    "record": recordid,
                    "field": field[ID],
                    "format": field[FORMAT],
                    "keys": self.formatconvert.keys(),
                },
            )
