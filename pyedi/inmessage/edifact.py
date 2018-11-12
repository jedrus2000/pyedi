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
    readdata_bin,
    logger,
    logmap,
    runscript,
)
import pyedi.outmessage as outmessage

from .var import Var


class Edifact(Var):
    """ class for edifact inmessage objects."""

    @staticmethod
    def _manipulatemessagetype(messagetype, inode):
        """ default: just return messagetype. """
        return messagetype.replace(
            ".", "_"
        )  # older edifact messages have eg 90.1 as version...does not match with python imports...so convert this

    def _readcontent_edifile(self):
        """ read content of edifact file in memory.
            is read as binary. In _sniff determine charset; then decode according to charset
        """
        logger.debug('Read edi file "%(filename)s".', self.ta_info)
        self.rawinput = readdata_bin(
            filename=self.ta_info["filename"]
        )  # read as binary

    def _sniff(self):
        """ examine the beginning of edifact file for syntax parameters and charset. if (beginning of) edifact file is not correct: error.
            edifact file is read as binary. edifact have several charsets (UNOA, UNOC, UNOY).
            in processing is assumed: charset is ascii, uft-8 or some charset where 1char=1byte (eg iso-9959-1)
            (if other charset: would be easy to change. charset is in grammar, read/decode for charset, do parsing)
            Bots assumes: UNA-string contains NO extra CR/LF. (would be absurd; combination of: multiple UNA in file & using 'blocked' edifact.)
        """
        rawinput = self.rawinput[0:99].decode("iso-8859-1")
        # **************find first non-whitespace character
        rawinput = rawinput.lstrip()
        # **************check if UNA
        if rawinput.startswith("UNA"):
            has_una_string = True
            # read UNA; set syntax parameters from UNA
            count = 3
            try:
                for field in [
                    "sfield_sep",
                    "field_sep",
                    "decimaal",
                    "escape",
                    "reserve",
                    "record_sep",
                ]:
                    self.ta_info[field] = rawinput[count]
                    count += 1
            except IndexError:
                # plus some border cases; not possible if mailbag is used.
                raise InMessageError(_("[A53]: Edifact file contains only whitespace."))
            # option extra check: separators etc are never in [0-9-a-zA-Z].
            # UNA-string is done; loop until next not-space char
            rawinput = rawinput[count:].lstrip()
        else:
            has_una_string = False

        # **************expect UNB
        # loop over rawinput to extract segmenttag, used separators, etc.
        count2 = 0
        found_tag = ""
        found_charset = ""
        for char in rawinput:
            if char in self.ta_info["skip_char"]:
                continue
            if count2 <= 2:
                found_tag += char
            elif count2 == 3:
                found_field_sep = char
                if found_tag != "UNB":
                    # also: UNA too short. not possible if mailbag is used.
                    raise InMessageError(
                        _('[A54]: Found no "UNB" at the start of edifact file.')
                    )
            elif count2 <= 7:
                found_charset += char
            elif count2 == 8:
                found_sfield_sep = char
            else:
                self.ta_info["version"] = char
                break
            count2 += 1
        else:
            # if arrive here: to many <cr/lf>?
            raise InMessageError(
                _("[A55]: Problems with UNB-segment; encountered too many <CR/LF>.")
            )

        # set and/or verify separators
        if has_una_string:
            if (
                    found_field_sep != self.ta_info["field_sep"]
                    or found_sfield_sep != self.ta_info["sfield_sep"]
            ):
                raise InMessageError(
                    _(
                        "[A56]: Separators used in edifact file differ from values indicated in UNA-segment."
                    )
                )
        else:
            if (
                    found_field_sep == "+" and found_sfield_sep == ":"
            ):  # assume standard/UNOA separators.
                self.ta_info["sfield_sep"] = ":"
                self.ta_info["field_sep"] = "+"
                self.ta_info["decimaal"] = "."
                self.ta_info["escape"] = "?"
                self.ta_info["reserve"] = "*"
                self.ta_info["record_sep"] = "'"
            elif (
                    found_field_sep == "\x1D" and found_sfield_sep == "\x1F"
            ):  # check if UNOB separators are used
                self.ta_info["sfield_sep"] = "\x1F"
                self.ta_info["field_sep"] = "\x1D"
                self.ta_info["decimaal"] = "."
                self.ta_info["escape"] = ""
                self.ta_info["reserve"] = "*"
                self.ta_info["record_sep"] = "\x1C"
            else:
                raise InMessageError(
                    _(
                        "[A57]: Edifact file with non-standard separators. An UNA segment should be used."
                    )
                )

        # *********** decode the file (to str)
        try:
            startUNB = self.rawinput.find(b"UNB")
            self.rawinput = self.rawinput[startUNB:].decode(
                found_charset, self.ta_info["checkcharsetin"]
            )
            self.ta_info["charset"] = found_charset
        except LookupError:
            _exception = InMessageError(
                _('[A58]: Edifact file has unknown characterset "%(charset)s".'),
                {"charset": found_charset},
            )
            _exception.__cause__ = None
            raise _exception
        # ~ except UnicodeDecodeError as msg:
        # ~ raise InMessageError(_('[A59]: Edifact file has not allowed characters at/after file-position %(content)s.'),
        # ~ {'content':msg[2]})
        # repetition separator only for version >= 4.
        if self.ta_info["version"] < "4" or self.ta_info["reserve"] == " ":
            # if version > 4 and repetition separator is
            # space: assume this is a mistake; use
            # repetition separator
            self.ta_info["reserve"] = ""
        self.separatorcheck(
            self.ta_info["sfield_sep"]
            + self.ta_info["field_sep"]
            + self.ta_info["decimaal"]
            + self.ta_info["escape"]
            + self.ta_info["reserve"]
            + self.ta_info["record_sep"]
        )

    def checkenvelope(self):
        """ check envelopes (UNB-UNZ counters & references, UNH-UNT counters & references etc)
        """
        for nodeunb in self.getloop({"BOTSID": "UNB"}):
            logmap.debug("Start parsing edifact envelopes")
            unbreference = nodeunb.get({"BOTSID": "UNB", "0020": None})
            unzreference = nodeunb.get(
                {"BOTSID": "UNB"}, {"BOTSID": "UNZ", "0020": None}
            )
            if unbreference and unzreference and unbreference != unzreference:
                self.add2errorlist(
                    _(
                        '[E01]: UNB-reference is "%(unbreference)s"; should be equal to UNZ-reference "%(unzreference)s".\n'
                    )
                    % {"unbreference": unbreference, "unzreference": unzreference}
                )
            unzcount = nodeunb.get({"BOTSID": "UNB"}, {"BOTSID": "UNZ", "0036": None})
            messagecount = len(nodeunb.children) - 1
            try:
                if int(unzcount) != messagecount:
                    self.add2errorlist(
                        _(
                            "[E02]: Count of messages in UNZ is %(unzcount)s; should be equal to number of messages %(messagecount)s.\n"
                        )
                        % {"unzcount": unzcount, "messagecount": messagecount}
                    )
            except:
                self.add2errorlist(
                    _('[E03]: Count of messages in UNZ is invalid: "%(count)s".\n')
                    % {"count": unzcount}
                )
            for nodeunh in nodeunb.getloop({"BOTSID": "UNB"}, {"BOTSID": "UNH"}):
                unhreference = nodeunh.get({"BOTSID": "UNH", "0062": None})
                untreference = nodeunh.get(
                    {"BOTSID": "UNH"}, {"BOTSID": "UNT", "0062": None}
                )
                if unhreference and untreference and unhreference != untreference:
                    self.add2errorlist(
                        _(
                            '[E04]: UNH-reference is "%(unhreference)s"; should be equal to UNT-reference "%(untreference)s".\n'
                        )
                        % {"unhreference": unhreference, "untreference": untreference}
                    )
                untcount = nodeunh.get(
                    {"BOTSID": "UNH"}, {"BOTSID": "UNT", "0074": None}
                )
                segmentcount = nodeunh.getcount()
                try:
                    if int(untcount) != segmentcount:
                        self.add2errorlist(
                            _(
                                "[E05]: Segmentcount in UNT is %(untcount)s; should be equal to number of segments %(segmentcount)s.\n"
                            )
                            % {"untcount": untcount, "segmentcount": segmentcount}
                        )
                except:
                    self.add2errorlist(
                        _('[E06]: Count of segments in UNT is invalid: "%(count)s".\n')
                        % {"count": untcount}
                    )
            for nodeung in nodeunb.getloop({"BOTSID": "UNB"}, {"BOTSID": "UNG"}):
                ungreference = nodeung.get({"BOTSID": "UNG", "0048": None})
                unereference = nodeung.get(
                    {"BOTSID": "UNG"}, {"BOTSID": "UNE", "0048": None}
                )
                if ungreference and unereference and ungreference != unereference:
                    self.add2errorlist(
                        _(
                            '[E07]: UNG-reference is "%(ungreference)s"; should be equal to UNE-reference "%(unereference)s".\n'
                        )
                        % {"ungreference": ungreference, "unereference": unereference}
                    )
                unecount = nodeung.get(
                    {"BOTSID": "UNG"}, {"BOTSID": "UNE", "0060": None}
                )
                groupcount = len(nodeung.children) - 1
                try:
                    if int(unecount) != groupcount:
                        self.add2errorlist(
                            _(
                                "[E08]: Groupcount in UNE is %(unecount)s; should be equal to number of groups %(groupcount)s.\n"
                            )
                            % {"unecount": unecount, "groupcount": groupcount}
                        )
                except:
                    self.add2errorlist(
                        _('[E09]: Groupcount in UNE is invalid: "%(count)s".\n')
                        % {"count": unecount}
                    )
                for nodeunh in nodeung.getloop({"BOTSID": "UNG"}, {"BOTSID": "UNH"}):
                    unhreference = nodeunh.get({"BOTSID": "UNH", "0062": None})
                    untreference = nodeunh.get(
                        {"BOTSID": "UNH"}, {"BOTSID": "UNT", "0062": None}
                    )
                    if unhreference and untreference and unhreference != untreference:
                        self.add2errorlist(
                            _(
                                '[E10]: UNH-reference is "%(unhreference)s"; should be equal to UNT-reference "%(untreference)s".\n'
                            )
                            % {
                                "unhreference": unhreference,
                                "untreference": untreference,
                            }
                        )
                    untcount = nodeunh.get(
                        {"BOTSID": "UNH"}, {"BOTSID": "UNT", "0074": None}
                    )
                    segmentcount = nodeunh.getcount()
                    try:
                        if int(untcount) != segmentcount:
                            self.add2errorlist(
                                _(
                                    "[E11]: Segmentcount in UNT is %(untcount)s; should be equal to number of segments %(segmentcount)s.\n"
                                )
                                % {"untcount": untcount, "segmentcount": segmentcount}
                            )
                    except:
                        self.add2errorlist(
                            _(
                                '[E12]: Count of segments in UNT is invalid: "%(count)s".\n'
                            )
                            % {"count": untcount}
                        )
            logmap.debug("Parsing edifact envelopes is OK")

    def handleconfirm(self, ta_fromfile, routedict, error):
        """ done at end of edifact file handling.
            generates CONTRL messages (or not)
        """
        # for fatal errors there is no decent node tree
        if self.errorfatal:
            return
        # check if there are any 'send-edifact-CONTRL' confirmrules.
        confirmtype = "send-edifact-CONTRL"
        if not globalcheckconfirmrules(confirmtype):
            return
        editype = "edifact"  # self.__class__.__name__
        AcknowledgeCode = "7" if not error else "4"
        for nodeunb in self.getloop({"BOTSID": "UNB"}):
            sender = nodeunb.get({"BOTSID": "UNB", "S002.0004": None})
            receiver = nodeunb.get({"BOTSID": "UNB", "S003.0010": None})
            nr_message_to_confirm = 0
            messages_not_confirm = []
            for nodeunh in nodeunb.getloop({"BOTSID": "UNB"}, {"BOTSID": "UNH"}):
                messagetype = nodeunh.queries["messagetype"]
                # no CONTRL for CONTRL or APERAK message; check if CONTRL should be send via confirmrules
                if messagetype[:6] in ["CONTRL", "APERAK"] or not checkconfirmrules(
                        confirmtype,
                        idroute=self.ta_info["idroute"],
                        idchannel=self.ta_info["fromchannel"],
                        frompartner=sender,
                        topartner=receiver,
                        messagetype=messagetype,
                ):
                    messages_not_confirm.append(nodeunh)
                else:
                    nr_message_to_confirm += 1
            if not nr_message_to_confirm:
                continue
            # remove message not to be confirmed from tree (is destructive, but this is end of file processing anyway.
            for message_not_confirm in messages_not_confirm:
                nodeunb.children.remove(message_not_confirm)
            # check if there is a user mappingscript
            tscript, toeditype, tomessagetype = lookup_translation(
                fromeditype=editype,
                frommessagetype="CONTRL",
                frompartner=receiver,
                topartner=sender,
                alt="",
            )
            if not tscript:
                tomessagetype = "CONTRL22UNEAN002"  # default messagetype for CONTRL
                translationscript = None
            else:
                translationscript, scriptfilename = botsimport(
                    "mappings", editype, tscript
                )  # import the mappingscript
            # generate CONTRL-message. One received interchange->one CONTRL-message
            reference = str(unique("messagecounter"))
            ta_confirmation = ta_fromfile.copyta(status=TRANSLATED)
            filename = str(ta_confirmation.idta)
            out = outmessage.outmessage_init(
                editype=editype,
                messagetype=tomessagetype,
                filename=filename,
                reference=reference,
                statust=OK,
            )  # make outmessage object
            out.ta_info["frompartner"] = receiver  # reverse!
            out.ta_info["topartner"] = sender  # reverse!
            if translationscript and hasattr(translationscript, "main"):
                runscript(
                    translationscript,
                    scriptfilename,
                    "main",
                    inn=self,
                    out=out,
                    routedict=routedict,
                    ta_fromfile=ta_fromfile,
                )
            else:
                # default mapping script for CONTRL
                # write UCI for UNB (envelope)
                out.put(
                    {
                        "BOTSID": "UNH",
                        "0062": reference,
                        "S009.0065": "CONTRL",
                        "S009.0052": "2",
                        "S009.0054": "2",
                        "S009.0051": "UN",
                        "S009.0057": "EAN002",
                    }
                )
                out.put({"BOTSID": "UNH"}, {"BOTSID": "UCI", "0083": AcknowledgeCode})
                out.put(
                    {"BOTSID": "UNH"},
                    {
                        "BOTSID": "UCI",
                        "0020": nodeunb.get({"BOTSID": "UNB", "0020": None}),
                    },
                )
                out.put(
                    {"BOTSID": "UNH"}, {"BOTSID": "UCI", "S002.0004": sender}
                )  # not reverse!
                out.put(
                    {"BOTSID": "UNH"},
                    {
                        "BOTSID": "UCI",
                        "S002.0007": nodeunb.get({"BOTSID": "UNB", "S002.0007": None}),
                    },
                )
                out.put(
                    {"BOTSID": "UNH"},
                    {
                        "BOTSID": "UCI",
                        "S002.0008": nodeunb.get({"BOTSID": "UNB", "S002.0008": None}),
                    },
                )
                out.put(
                    {"BOTSID": "UNH"},
                    {
                        "BOTSID": "UCI",
                        "S002.0042": nodeunb.get({"BOTSID": "UNB", "S002.0042": None}),
                    },
                )
                out.put(
                    {"BOTSID": "UNH"}, {"BOTSID": "UCI", "S003.0010": receiver}
                )  # not reverse!
                out.put(
                    {"BOTSID": "UNH"},
                    {
                        "BOTSID": "UCI",
                        "S003.0007": nodeunb.get({"BOTSID": "UNB", "S003.0007": None}),
                    },
                )
                out.put(
                    {"BOTSID": "UNH"},
                    {
                        "BOTSID": "UCI",
                        "S003.0014": nodeunb.get({"BOTSID": "UNB", "S003.0014": None}),
                    },
                )
                out.put(
                    {"BOTSID": "UNH"},
                    {
                        "BOTSID": "UCI",
                        "S003.0046": nodeunb.get({"BOTSID": "UNB", "S003.0046": None}),
                    },
                )
                # write UCM for each UNH (message)
                for nodeunh in nodeunb.getloop({"BOTSID": "UNB"}, {"BOTSID": "UNH"}):
                    lou = out.putloop({"BOTSID": "UNH"}, {"BOTSID": "UCM"})
                    lou.put({"BOTSID": "UCM", "0083": AcknowledgeCode})
                    lou.put(
                        {
                            "BOTSID": "UCM",
                            "0062": nodeunh.get({"BOTSID": "UNH", "0062": None}),
                        }
                    )
                    lou.put(
                        {
                            "BOTSID": "UCM",
                            "S009.0065": nodeunh.get(
                                {"BOTSID": "UNH", "S009.0065": None}
                            ),
                        }
                    )
                    lou.put(
                        {
                            "BOTSID": "UCM",
                            "S009.0052": nodeunh.get(
                                {"BOTSID": "UNH", "S009.0052": None}
                            ),
                        }
                    )
                    lou.put(
                        {
                            "BOTSID": "UCM",
                            "S009.0054": nodeunh.get(
                                {"BOTSID": "UNH", "S009.0054": None}
                            ),
                        }
                    )
                    lou.put(
                        {
                            "BOTSID": "UCM",
                            "S009.0051": nodeunh.get(
                                {"BOTSID": "UNH", "S009.0051": None}
                            ),
                        }
                    )
                    lou.put(
                        {
                            "BOTSID": "UCM",
                            "S009.0057": nodeunh.get(
                                {"BOTSID": "UNH", "S009.0057": None}
                            ),
                        }
                    )
                # last line (counts the segments produced in out-message)
                out.put(
                    {"BOTSID": "UNH"},
                    {"BOTSID": "UNT", "0074": out.getcount() + 1, "0062": reference},
                )
                # try to run the user mapping script fuction 'change' (after the default
                # mapping); 'chagne' fucntion recieves the tree as written by default
                # mapping, function can change tree.
                if translationscript and hasattr(translationscript, "change"):
                    runscript(
                        translationscript,
                        scriptfilename,
                        "change",
                        inn=self,
                        out=out,
                        routedict=routedict,
                        ta_fromfile=ta_fromfile,
                    )
            # write tomessage (result of translation)
            out.writeall()
            logger.debug(
                'Send edifact confirmation (CONTRL) route "%(route)s" fromchannel "%(fromchannel)s" frompartner "%(frompartner)s" topartner "%(topartner)s".',
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

    def try_to_retrieve_info(self):
        """ when edi-file is not correct, (try to) get info about eg partnerID's in message
            for now: look around in lexed record
        """
        if hasattr(self, "lex_records"):
            for lex_record in self.lex_records:
                if lex_record[0][VALUE] == "UNB":
                    count_fields = 0
                    for field in lex_record:
                        if not field[SFIELD]:  # if field (not subfield etc)
                            count_fields += 1
                            if count_fields == 3:
                                self.ta_info["frompartner"] = field[VALUE]
                            elif count_fields == 4:
                                self.ta_info["topartner"] = field[VALUE]
                            elif count_fields == 6:
                                self.ta_info["reference"] = field[VALUE]
                                return
                    return


