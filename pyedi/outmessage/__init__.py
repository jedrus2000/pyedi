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
from gettext import gettext as _

from pyedi.botslib import OutMessageError
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
from .fixed import Fixed
from .idoc import Idoc
from .templatehtml import TemplateHtml

out_msg_classes = {
    'csv': Csv,
    'db': Db,
    'edifact': Edifact,
    'fixed': Fixed,
    'idoc': Idoc,
    'jsonnocheck': JsonNoCheck,
    'json': Json,
    'raw': Raw,
    'templatehtml': TemplateHtml,
    'tradacoms': Tradacoms,
    'xmlnocheck': XmlNoCheck,
    'xml': Xml,
    'x12': X12
}


def outmessage_init(**ta_info):
    """ dispatch function class Outmessage or subclass
        ta_info: needed is editype, messagetype, filename, charset, merge
    """
    try:
        classtocall = out_msg_classes.get(ta_info["editype"])
    except KeyError:
        raise OutMessageError(
            _("Unknown editype for outgoing message: %(editype)s"), ta_info
        )
    return classtocall(ta_info)
