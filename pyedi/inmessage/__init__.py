from gettext import gettext as _

# bots-modules

from pyedi.botslib import (
    query,
    txtexc,
    get_relevant_text_for_UnicodeError,
    InMessageError,
    config,
)

from .raw import Raw
from .db import Db
from .jsonnocheck import JsonNoCheck
from .json import Json
from .xmlnocheck import XmlNoCheck
from .xml import Xml
from .tradacoms import Tradacoms
from .x12 import X12
from .csv import Csv
from .edifact import Edifact
from .excel import Excel
from .fixed import Fixed
from .idoc import Idoc

in_msg_classes = {
    'csv': Csv,
    'db': Db,
    'edifact': Edifact,
    'excel': Excel,
    'fixed': Fixed,
    'idoc': Idoc,
    'jsonnocheck': JsonNoCheck,
    'json': Json,
    'raw': Raw,
    'tradacoms': Tradacoms,
    'xmlnocheck': XmlNoCheck,
    'xml': Xml,
    'x12': X12
}

""" Reading/lexing/parsing/splitting an edifile."""
def parse_edi_file(**ta_info):
    """ Read,lex, parse edi-file. Is a dispatch function for InMessage and subclasses.
        Error handling: there are different types of errors.
        For all errors related to incoming messages: catch these.
        Try to extract the relevant information for the message.
        - str errors: charset is wrong.
    """
    try:
        classtocall = in_msg_classes.get(ta_info["editype"])  # get inmessage class to call (subclass of InMessage)
        ediobject = classtocall(ta_info)
    except KeyError:
        raise InMessageError(
            _("Unknown editype for incoming message: %(editype)s"), ta_info
        )
    # read, lex, parse the incoming edi file
    # ALL errors are caught; these are 'fatal errors': processing has stopped.
    # get information from error/exception; format this into ediobject.errorfatal
    try:
        ediobject.initfromfile()
    except UnicodeError as e:
        # ~ raise botslib.MessageError('')      #UNITTEST_CORRECTION
        content = get_relevant_text_for_UnicodeError(e)
        # msg.encoding should contain encoding, but does not (think this is not OK for UNOA, etc)
        ediobject.errorlist.append(
            str(
                InMessageError(
                    _(
                        '[A59]: incoming file has not allowed characters at/after file-position %(pos)s: "%(content)s".'
                    ),
                    {"pos": e.start, "content": content},
                )
            )
        )
    except Exception as e:
        # ~ raise botslib.MessageError('')      #UNITTEST_CORRECTION
        txt = txtexc()
        if not config.get(["settings", "debug"]):
            txt = txt.partition(": ")[2]
        ediobject.errorlist.append(txt)
    else:
        ediobject.errorfatal = False
    return ediobject


def lookup_translation(frommessagetype, fromeditype, alt, frompartner, topartner):
    """ lookup the translation: frommessagetype,fromeditype,alt,frompartner,topartner -> mappingscript, tomessagetype, toeditype
    """
    for row2 in query(
            """SELECT tscript,tomessagetype,toeditype
                                FROM translate
                                WHERE frommessagetype = %(frommessagetype)s
                                AND fromeditype = %(fromeditype)s
                                AND active=%(booll)s
                                AND (alt='' OR alt=%(alt)s)
                                AND (frompartner_id IS NULL OR frompartner_id=%(frompartner)s OR frompartner_id in (SELECT to_partner_id
                                                                                                                        FROM partnergroup
                                                                                                                        WHERE from_partner_id=%(frompartner)s ))
                                AND (topartner_id IS NULL OR topartner_id=%(topartner)s OR topartner_id in (SELECT to_partner_id
                                                                                                                FROM partnergroup
                                                                                                                WHERE from_partner_id=%(topartner)s ))
                                ORDER BY alt DESC,
                                         CASE WHEN frompartner_id IS NULL THEN 1 ELSE 0 END, frompartner_id ,
                                         CASE WHEN topartner_id IS NULL THEN 1 ELSE 0 END, topartner_id """,
            {
                "frommessagetype": frommessagetype,
                "fromeditype": fromeditype,
                "alt": alt,
                "frompartner": frompartner,
                "topartner": topartner,
                "booll": True,
            },
    ):
        return row2[str("tscript")], row2[str("toeditype")], row2[str("tomessagetype")]
        # translation is found; only the first one is used - this is what the ORDER BY in the query takes care of
    else:  # no translation found in translate table
        return None, None, None
