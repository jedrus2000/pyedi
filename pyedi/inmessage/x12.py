"""
This is modified code of Bots project:
    http://bots.sourceforge.net/en/index.shtml
    ttp://bots.readthedocs.io
    https://github.com/eppye-bots/bots

originally created by Henk-Jan Ebbers.

This code include also changes from other forks, specially from:
    https://github.com/bots-edi

This project, as original Bots is licenced under GNU GENERAL PUBLIC LICENSE Version 3; for full
text: http://www.gnu.org/copyleft/gpl.html
"""

try:
    from xml.etree import cElementTree as ET
except ImportError:
    from xml.etree import ElementTree as ET

from gettext import gettext as _

# bots-modules

from pyedi.botslib.consts import *
from pyedi.botslib import (
    globalcheckconfirmrules,
    unique,
    InMessageError,
    checkconfirmrules,
    botsimport,
    logger,
    logmap,
    runscript,
)
import pyedi.outmessage as outmessage

from .var import Var


class X12(Var):
    """ class for x12 inmessage objects."""

    @staticmethod
    def _manipulatemessagetype(messagetype, inode):
        """ x12 also needs field from GS record to identify correct messagetype """
        return messagetype + inode.record.get("GS08", "")

    def _sniff(self):
        """ examine a file for syntax parameters and correctness of protocol
            eg parse ISA, get charset and version
        """
        count = 0
        version = ""
        recordID = ""
        rawinput = self.rawinput[:200].lstrip()
        for char in rawinput:
            if char in "\r\n" and count != 105:  # pos 105: is record_sep, could be \r\n
                continue
            count += 1
            if count <= 3:
                recordID += char
            elif count == 4:
                self.ta_info["field_sep"] = char
                if recordID != "ISA":
                    raise InMessageError(
                        _('[A60]: Expect "ISA", found "%(content)s". Probably no x12?'),
                        {"content": self.rawinput[:7]},
                    )  # not with mailbag
            elif count in [
                7,
                18,
                21,
                32,
                35,
                51,
                54,
                70,
            ]:  # extra checks for fixed ISA.
                if char != self.ta_info["field_sep"]:
                    raise InMessageError(
                        _(
                            '[A63]: Non-valid ISA header; position %(pos)s of ISA is "%(foundchar)s", expect here element separator "%(field_sep)s".'
                        ),
                        {
                            "pos": str(count),
                            "foundchar": char,
                            "field_sep": self.ta_info["field_sep"],
                        },
                    )
            elif count == 83:
                self.ta_info["reserve"] = char
            elif count < 85:
                continue
            elif count <= 89:
                version += char
            elif count == 105:
                self.ta_info["sfield_sep"] = char
            elif count == 106:
                self.ta_info["record_sep"] = char
                break
        else:
            # if arrive here: not not reach count == 106.
            if count == 0:
                raise InMessageError(
                    _("[A61]: Edi file contains only whitespace.")
                )  # not with mailbag
            else:
                raise InMessageError(
                    _("[A62]: Expect X12 file but envelope is not right.")
                )
        # Note: reserve=repeating separator.
        # Since ISA version 00403 used as repeat sep. Some partners use ISA version above 00403 but do not use repeats. Than this char is eg 'U' (as in older ISA versions).
        # This wrong usage is caugth by checking if the char is alfanumeric; if so
        # assume wrong usage (and do not use repeat sep.)
        if version < "00403" or self.ta_info["reserve"].isalnum():
            self.ta_info["reserve"] = ""
        # if <CR> is segment terminator: cannot be in the skip_char-string!
        self.ta_info["skip_char"] = self.ta_info["skip_char"].replace(
            self.ta_info["record_sep"], ""
        )
        self.separatorcheck(
            self.ta_info["sfield_sep"]
            + self.ta_info["field_sep"]
            + self.ta_info["reserve"]
            + self.ta_info["record_sep"]
        )

    def checkenvelope(self):
        """ check envelopes, gather information to generate 997 """
        for nodeisa in self.getloop({"BOTSID": "ISA"}):
            logmap.debug("Start parsing X12 envelopes")
            isareference = nodeisa.get({"BOTSID": "ISA", "ISA13": None})
            ieareference = nodeisa.get(
                {"BOTSID": "ISA"}, {"BOTSID": "IEA", "IEA02": None}
            )
            if isareference and ieareference and isareference != ieareference:
                self.add2errorlist(
                    _(
                        '[E13]: ISA-reference is "%(isareference)s"; should be equal to IEA-reference "%(ieareference)s".\n'
                    )
                    % {"isareference": isareference, "ieareference": ieareference}
                )
            ieacount = nodeisa.get({"BOTSID": "ISA"}, {"BOTSID": "IEA", "IEA01": None})
            groupcount = nodeisa.getcountoccurrences(
                {"BOTSID": "ISA"}, {"BOTSID": "GS"}
            )
            try:
                if int(ieacount) != groupcount:
                    self.add2errorlist(
                        _(
                            "[E14]: Count in IEA-IEA01 is %(ieacount)s; should be equal to number of groups %(groupcount)s.\n"
                        )
                        % {"ieacount": ieacount, "groupcount": groupcount}
                    )
            except:
                self.add2errorlist(
                    _('[E15]: Count of messages in IEA is invalid: "%(count)s".\n')
                    % {"count": ieacount}
                )
            for nodegs in nodeisa.getloop({"BOTSID": "ISA"}, {"BOTSID": "GS"}):
                gsreference = nodegs.get({"BOTSID": "GS", "GS06": None})
                gereference = nodegs.get(
                    {"BOTSID": "GS"}, {"BOTSID": "GE", "GE02": None}
                )
                if gsreference and gereference and gsreference != gereference:
                    self.add2errorlist(
                        _(
                            '[E16]: GS-reference is "%(gsreference)s"; should be equal to GE-reference "%(gereference)s".\n'
                        )
                        % {"gsreference": gsreference, "gereference": gereference}
                    )
                gecount = nodegs.get({"BOTSID": "GS"}, {"BOTSID": "GE", "GE01": None})
                messagecount = len(nodegs.children) - 1
                try:
                    if int(gecount) != messagecount:
                        self.add2errorlist(
                            _(
                                "[E17]: Count in GE-GE01 is %(gecount)s; should be equal to number of transactions: %(messagecount)s.\n"
                            )
                            % {"gecount": gecount, "messagecount": messagecount}
                        )
                except:
                    self.add2errorlist(
                        _('[E18]: Count of messages in GE is invalid: "%(count)s".\n')
                        % {"count": gecount}
                    )
                for nodest in nodegs.getloop({"BOTSID": "GS"}, {"BOTSID": "ST"}):
                    streference = nodest.get({"BOTSID": "ST", "ST02": None})
                    sereference = nodest.get(
                        {"BOTSID": "ST"}, {"BOTSID": "SE", "SE02": None}
                    )
                    # referencefields are numerical; should I compare values??
                    if streference and sereference and streference != sereference:
                        self.add2errorlist(
                            _(
                                '[E19]: ST-reference is "%(streference)s"; should be equal to SE-reference "%(sereference)s".\n'
                            )
                            % {"streference": streference, "sereference": sereference}
                        )
                    secount = nodest.get(
                        {"BOTSID": "ST"}, {"BOTSID": "SE", "SE01": None}
                    )
                    segmentcount = nodest.getcount()
                    try:
                        if int(secount) != segmentcount:
                            self.add2errorlist(
                                _(
                                    "[E20]: Count in SE-SE01 is %(secount)s; should be equal to number of segments %(segmentcount)s.\n"
                                )
                                % {"secount": secount, "segmentcount": segmentcount}
                            )
                    except:
                        self.add2errorlist(
                            _(
                                '[E21]: Count of segments in SE is invalid: "%(count)s".\n'
                            )
                            % {"count": secount}
                        )
            logmap.debug("Parsing X12 envelopes is TransactionStatus.OK")

    def try_to_retrieve_info(self):
        """ when edi-file is not correct, (try to) get info about eg partnerID's in message
            for now: look around in lexed record
        """
        if hasattr(self, "lex_records"):
            for lex_record in self.lex_records:
                if lex_record[0][VALUE] == "ISA":
                    count_fields = 0
                    for field in lex_record:
                        count_fields += 1
                        if count_fields == 7:
                            self.ta_info["frompartner"] = field[VALUE]
                        elif count_fields == 9:
                            self.ta_info["topartner"] = field[VALUE]
                        elif count_fields == 15:
                            self.ta_info["reference"] = field[VALUE]
                            return
                    return

    def handleconfirm(self, ta_fromfile, routedict, error):
        """ at end of edi file handling:
            send 997 messages (or not)
        """
        # for fatal errors there is no decent node tree
        if self.errorfatal:
            return
        # check if there are any 'send-x12-997' confirmrules.
        confirmtype = "send-x12-997"
        if not globalcheckconfirmrules(confirmtype):
            return
        editype = "x12"  # self.__class__.__name__
        AcknowledgeCode = "A" if not error else "R"
        for nodegs in self.getloop({"BOTSID": "ISA"}, {"BOTSID": "GS"}):
            if (
                    nodegs.get({"BOTSID": "GS", "GS01": None}) == "FA"
            ):  # do not generate 997 for 997
                continue
            # get the partnerID's from received file
            sender = self.ta_info.get(
                "frompartner", nodegs.get({"BOTSID": "GS", "GS02": None})
            )
            receiver = self.ta_info.get(
                "topartner", nodegs.get({"BOTSID": "GS", "GS03": None})
            )
            nr_message_to_confirm = 0
            messages_not_confirm = []
            for nodest in nodegs.getloop({"BOTSID": "GS"}, {"BOTSID": "ST"}):
                messagetype = nodest.queries["messagetype"]
                if not checkconfirmrules(
                        confirmtype,
                        idroute=self.ta_info["idroute"],
                        idchannel=self.ta_info["fromchannel"],
                        frompartner=sender,
                        topartner=receiver,
                        messagetype=messagetype,
                ):
                    messages_not_confirm.append(nodest)
                else:
                    nr_message_to_confirm += 1
            if not nr_message_to_confirm:
                continue
            # remove message not to be confirmed from tree (is destructive, but this is end of file processing anyway.
            for message_not_confirm in messages_not_confirm:
                nodegs.children.remove(message_not_confirm)
            # check if there is a user mappingscript
            tscript, toeditype, tomessagetype = lookup_translation(
                fromeditype=editype,
                frommessagetype="997",
                frompartner=receiver,
                topartner=sender,
                alt="",
            )
            if not tscript:
                tomessagetype = "997004010"  # default messagetype for 997
                translationscript = None
            else:
                translationscript, scriptfilename = botsimport(
                    "mappings", editype, tscript
                )  # import the mappingscript
            # generate 997. For each GS-GE->one 997
            # 20120411: use zfill as messagescounter can be <1000, ST02 field is min 4 positions
            reference = str(unique("messagecounter")).zfill(4)
            ta_confirmation = ta_fromfile.copyta(status=TRANSLATED)
            filename = str(ta_confirmation.idta)
            out = outmessage.outmessage_init(
                editype=editype,
                messagetype=tomessagetype,
                filename=filename,
                reference=reference,
                statust=TransactionStatus.OK,
            )  # make outmessage object
            out.ta_info["frompartner"] = receiver  # reverse!
            out.ta_info["topartner"] = sender  # reverse!
            if translationscript and hasattr(translationscript, "main"):
                runscript(
                    translationscript,
                    scriptfilename,
                    "main",
                    inn=nodegs,
                    out=out,
                    routedict=routedict,
                    ta_fromfile=ta_fromfile,
                )
            else:
                # default mapping script for 997
                # write AK1/AK9 for GS (envelope)
                out.put({"BOTSID": "ST", "ST01": "997", "ST02": reference})
                out.put(
                    {"BOTSID": "ST"},
                    {
                        "BOTSID": "AK1",
                        "AK101": nodegs.get({"BOTSID": "GS", "GS01": None}),
                        "AK102": nodegs.get({"BOTSID": "GS", "GS06": None}),
                    },
                )
                gecount = nodegs.get({"BOTSID": "GS"}, {"BOTSID": "GE", "GE01": None})
                out.put(
                    {"BOTSID": "ST"},
                    {
                        "BOTSID": "AK9",
                        "AK901": AcknowledgeCode,
                        "AK902": gecount,
                        "AK903": gecount,
                        "AK904": gecount,
                    },
                )
                # write AK2 for each ST (message)
                for nodest in nodegs.getloop({"BOTSID": "GS"}, {"BOTSID": "ST"}):
                    lou = out.putloop({"BOTSID": "ST"}, {"BOTSID": "AK2"})
                    lou.put(
                        {
                            "BOTSID": "AK2",
                            "AK201": nodest.get({"BOTSID": "ST", "ST01": None}),
                            "AK202": nodest.get({"BOTSID": "ST", "ST02": None}),
                        }
                    )
                    lou.put(
                        {"BOTSID": "AK2"}, {"BOTSID": "AK5", "AK501": AcknowledgeCode}
                    )
                # last line (counts the segments produced in out-message)
                out.put(
                    {"BOTSID": "ST"},
                    {"BOTSID": "SE", "SE01": out.getcount() + 1, "SE02": reference},
                )
                # try to run the user mapping script fuction 'change' (after the default
                # mapping); 'chagne' fucntion recieves the tree as written by default
                # mapping, function can change tree.
                if translationscript and hasattr(translationscript, "change"):
                    runscript(
                        translationscript,
                        scriptfilename,
                        "change",
                        inn=nodegs,
                        out=out,
                        routedict=routedict,
                        ta_fromfile=ta_fromfile,
                    )
            # write tomessage (result of translation)
            out.writeall()  # write tomessage (result of translation)
            logger.debug(
                'Send x12 confirmation (997) route "%(route)s" fromchannel "%(fromchannel)s" frompartner "%(frompartner)s" topartner "%(topartner)s".',
                {
                    "route": self.ta_info["idroute"],
                    "fromchannel": self.ta_info["fromchannel"],
                    "frompartner": receiver,
                    "topartner": sender,
                },
            )
            # this info is used in transform.py to update the ta.....ugly...
            self.ta_info.update(
                confirmtype=confirmtype,
                confirmed=True,
                confirmasked=True,
                confirmidta=ta_confirmation.idta,
            )
            ta_confirmation.update(**out.ta_info)  # update ta for confirmation
