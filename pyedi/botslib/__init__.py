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

from .config import config
from .calling import runscript
from .transactions import log_session, OldTransaction
from .exceptions import (
    txtexc,
    get_relevant_text_for_UnicodeError,
    MessageRootError,
    MappingFormatError,
    MappingRootError,
    BotsError,
    InMessageError,
    MessageError,
    BotsImportError,
    FileTooLargeError,
    GotoException,
    TranslationNotFoundError,
    GrammarError,
    GrammarPartMissing,
    OutMessageError,
)
from .importtools import botsimport, botsbaseimport
from .logger import logger, logmap
from .misc import updateunlessset, indent_xml
from .filetools import (
    readdata_pickled,
    abspathdata,
    writedata_pickled,
    abspath,
)
from .confirmrules import (
    prepare_confirmrules,
    set_asked_confirmrules,
    globalcheckconfirmrules,
    checkconfirmrules,
)
from .database import (
    unique,
    query,
    changeq,
    insertta,
)

from .storage import (
    EdiStorage,
    EdiFile,
    FileSystemStorage,
)

from .globals import (
    setrouteid,
    getrouteid,
)

