import collections
import traceback

from pyedi.botslib.strings import safe_unicode
from pyedi.botslib.config import config


def get_relevant_text_for_UnicodeError(msg):
    """ see python doc for details of UnicodeError"""
    start = msg.start - 10 if msg.start >= 10 else 0
    return msg.object[start : msg.end + 35]


def txtexc():
    """ Process last exception, get an errortext.
        Errortext should be valid unicode.
    """
    if config.get(["settings", "debug"], False):
        return safe_unicode(traceback.format_exc(limit=None))
    else:
        terug = safe_unicode(traceback.format_exc(limit=0))
        terug = terug.replace("Traceback (most recent call last):\n", "")
        terug = terug.replace("bots.botslib.", "")
        return terug


class BotsError(Exception):
    """ formats the error messages. Under all circumstances: give (reasonable) output, no errors.
        input (msg,*args,**kwargs) can be anything: strings (any charset), unicode, objects. Note that these are errors, so input can be 'not valid'!
        to avoid the risk of 'errors during errors' catch-all solutions are used.
        2 ways to raise Exceptions:
        - BotsError('tekst %(var1)s %(var2)s',{'var1':'value1','var2':'value2'})  ###this one is preferred!!
        - BotsError('tekst %(var1)s %(var2)s',var1='value1',var2='value2')
    """

    def __init__(self, msg, *args, **kwargs):
        self.msg = safe_unicode(msg)
        if args:  # expect args[0] to be a dict
            if isinstance(args[0], dict):
                xxx = args[0]
            else:
                xxx = {}
        else:
            xxx = kwargs
        self.xxx = collections.defaultdict(str)
        for key, value in xxx.items():
            self.xxx[safe_unicode(key)] = safe_unicode(value)

    def __str__(self):
        try:
            return self.msg % (self.xxx)  # this is already unicode
        except:
            print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX11")
            return (
                self.msg
            )  # errors in self.msg; non supported format codes. Don't think this happen...


class CodeConversionError(BotsError):
    pass


class CommunicationError(BotsError):
    pass


class CommunicationInError(BotsError):
    pass


class CommunicationOutError(BotsError):
    pass


class EanError(BotsError):
    pass


class GrammarError(BotsError):
    pass


class GrammarPartMissing(BotsError):
    pass


class InMessageError(BotsError):
    pass


class LockedFileError(BotsError):
    pass


class MessageError(BotsError):
    pass


class MessageRootError(BotsError):
    pass


class MappingRootError(BotsError):
    pass


class MappingFormatError(BotsError):
    pass


class OutMessageError(BotsError):
    pass


class PanicError(BotsError):
    pass


class PersistError(BotsError):
    pass


class PluginError(BotsError):
    pass


class BotsImportError(
    BotsError
):  # import script or recursivly imported scripts not there
    pass


class ScriptImportError(BotsError):  # import errors in userscript; userscript is there
    pass


class ScriptError(BotsError):  # runtime errors in a userscript
    pass


class TraceError(BotsError):
    pass


class TranslationNotFoundError(BotsError):
    pass


class GotoException(
    BotsError
):  # sometimes it is simplest to raise an error, and catch it rightaway. Like a goto ;-)
    pass


class FileTooLargeError(BotsError):
    pass
