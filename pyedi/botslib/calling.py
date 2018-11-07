# **********************************************************/**
# *************************calling modules, programs***********************/**
# **********************************************************/**
from pyedi.botslib.logger import logger
from pyedi.botslib.exceptions import txtexc, ScriptError


def runscript(module, modulefile, functioninscript, **argv):
    """ Execute userscript. Functioninscript is supposed to be there; if not AttributeError is raised.
        Often is checked in advance if Functioninscript does exist.
    """
    logger.debug(
        'Run userscript "%(functioninscript)s" in "%(modulefile)s".',
        {"functioninscript": functioninscript, "modulefile": modulefile},
    )
    functiontorun = getattr(module, functioninscript)
    try:
        return functiontorun(**argv)
    except:
        txt = txtexc()
        _exception = ScriptError(
            _('Userscript "%(modulefile)s": "%(txt)s".'),
            {"modulefile": modulefile, "txt": txt},
        )
        _exception.__cause__ = None
        raise _exception


def tryrunscript(module, modulefile, functioninscript, **argv):
    if module and hasattr(module, functioninscript):
        runscript(module, modulefile, functioninscript, **argv)
        return True
    return False


def runscriptyield(module, modulefile, functioninscript, **argv):
    logger.debug(
        'Run userscript "%(functioninscript)s" in "%(modulefile)s".',
        {"functioninscript": functioninscript, "modulefile": modulefile},
    )
    functiontorun = getattr(module, functioninscript)
    try:
        for result in functiontorun(**argv):
            yield result
    except:
        txt = txtexc()
        _exception = ScriptError(
            _('Script file "%(modulefile)s": "%(txt)s".'),
            {"modulefile": modulefile, "txt": txt},
        )
        _exception.__cause__ = None
        raise _exception
