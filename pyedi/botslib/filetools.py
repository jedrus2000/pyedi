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
# **********************************************************/**
# *************************File handling os.path etc***********************/**
# **********************************************************/**
import os
import codecs
import pickle

from pyedi.botslib import (
    config,
)

def join(*paths):
    """Does does more as join.....
        - join the paths (compare os.path.join)
        - if path is not absolute, interpretate this as relative from bots directory.
        - normalize"""
    return os.path.normpath(
        os.path.join(config.get(["directories", "botspath"]), *paths)
    )


def dirshouldbethere(path):
    if path and not os.path.exists(path):
        os.makedirs(path)
        return True
    return False


def abspath(soort, filename):
    """ get absolute path for internal files; path is a section in bots.ini """
    directory = config.get(["directories", soort])
    return join(directory, filename)


def abspathdata(filename):
    """ abspathdata if filename incl dir: return absolute path; else (only filename): return absolute path (datadir)"""
    if "/" in filename:  # if filename already contains path
        return join(filename)
    else:
        directory = config.get(["directories", "data"])
        datasubdir = filename[:-3]
        if not datasubdir:
            datasubdir = "0"
        return join(directory, datasubdir, filename)


def deldata(filename):
    """ delete internal data file."""
    filename = abspathdata(filename)
    try:
        os.remove(filename)
    except:
        pass


def _opendata(filename, mode, charset, errors="strict"):
    """ open internal data file as unicode."""
    filename = abspathdata(filename)
    if "w" in mode:
        dirshouldbethere(os.path.dirname(filename))
    return codecs.open(filename, mode, charset, errors)


def _readdata(filename, charset, errors="strict"):
    """ read internal data file in memory as unicode."""
    filehandler = _opendata(filename, "r", charset, errors)
    content = filehandler.read()
    filehandler.close()
    return content


def _opendata_bin(filename, mode):
    """ open internal data file as binary."""
    filename = abspathdata(filename)
    if "w" in mode:
        dirshouldbethere(os.path.dirname(filename))
    return open(filename, mode)


def _readdata_bin(filename):
    """ read internal data file in memory as binary."""
    filehandler = _opendata_bin(filename, mode="rb")
    content = filehandler.read()
    filehandler.close()
    return content


def readdata_pickled(filename):
    filehandler = _opendata_bin(filename, mode="rb")  # pickle is a binary/byte stream
    content = pickle.load(filehandler)
    filehandler.close()
    return content


def writedata_pickled(filename, content):
    filehandler = _opendata_bin(filename, mode="wb")  # pickle is a binary/byte stream
    pickle.dump(content, filehandler)
    filehandler.close()
