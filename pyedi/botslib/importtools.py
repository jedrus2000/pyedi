# **********************************************************/**
# *************************import ***********************/**
# **********************************************************/**
import importlib
from gettext import gettext as _

from pyedi.botslib.exceptions import BotsImportError, ScriptImportError
from pyedi.botslib.config import config, PyEdiConfig
from pyedi.botslib.filetools import join
from pyedi.botslib.logger import logger


def botsbaseimport(modulename):
    """Do a dynamic import.
        Errors/exceptions are handled in calling functions.
    """
    return importlib.import_module(modulename)


def botsimport(*args):
    """ import modules from usersys.
        return: imported module, filename imported module;
        if not found or error in module: raise
    """
    modulepath = ".".join(
        (config.get([PyEdiConfig.DIRECTORIES, PyEdiConfig.USERSYSIMPORTPATH]),) + args
    )  # assemble import string
    # assemble abs filename for errortexts; note that 'join' is function in this script-file.
    modulefile = join(
        config.get([PyEdiConfig.DIRECTORIES, PyEdiConfig.USERSYSABS]), *args
    )
    # check if previous import failed (no need to try again).This eliminates eg lots of partner specific imports.
    if modulepath in config.get([PyEdiConfig.NOT_IMPORT]):
        logger.debug(
            _('No import of module "%(modulefile)s".'), {"modulefile": modulefile}
        )
        raise BotsImportError(
            _('No import of module "%(modulefile)s".'), {"modulefile": modulefile}
        )
    try:
        module = botsbaseimport(modulepath.lower())
    except ImportError as msg:
        config.add(PyEdiConfig.NOT_IMPORT, modulepath)
        logger.debug(
            _('No import of module "%(modulefile)s": %(txt)s.'),
            {"modulefile": modulefile, "txt": msg},
        )
        _exception = BotsImportError(
            _('No import of module "%(modulefile)s": %(txt)s'),
            {"modulefile": modulefile, "txt": msg},
        )
        _exception.__cause__ = None
        raise _exception
    except Exception as msg:
        logger.debug(
            _('Error in import of module "%(modulefile)s": %(txt)s.'),
            {"modulefile": modulefile, "txt": msg},
        )
        _exception = ScriptImportError(
            _('Error in import of module "%(modulefile)s":\n%(txt)s'),
            {"modulefile": modulefile, "txt": msg},
        )
        _exception.__cause__ = None
        raise _exception
    else:
        logger.debug('Imported "%(modulefile)s".', {"modulefile": modulefile})
        return module, modulefile
