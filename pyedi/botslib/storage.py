import codecs
import os
from abc import ABC, abstractmethod

from .filetools import dirshouldbethere

class EdiFile(ABC):
    def __init__(self, filename, mode, charset, check_charset_mode):
        self._filename = filename
        self._mode = mode
        self._charset = charset
        self._check_charset_mode = check_charset_mode

    @abstractmethod
    def open(self, filename, mode, charset, check_charset_mode):
        pass

    @abstractmethod
    def read(self):
        return ''

    @abstractmethod
    def write(self, value):
        pass

    @abstractmethod
    def close(self):
        pass


class EdiStorage(ABC):

    @abstractmethod
    def opendata(self, filename, mode, charset, check_charset_mode="strict"):
        """ open internal data file as unicode."""
        pass

    @abstractmethod
    def readdata(self, filename, charset, check_charset_mode="strict"):
        """ read internal data file in memory as unicode."""
        pass

    @abstractmethod
    def opendata_bin(self, filename, mode):
        """ open internal data file as binary."""
        pass

    @abstractmethod
    def readdata_bin(self, filename):
        """ read internal data file in memory as binary."""
        pass

#
# FileSystemStorage
#
class FileSystemStorage(EdiStorage):
    def opendata(self, filename, mode, charset, check_charset_mode="strict"):
        """ open internal data file as unicode."""
        if "w" in mode:
            dirshouldbethere(os.path.dirname(filename))
        return codecs.open(filename, mode, charset, check_charset_mode)

    def readdata(self, filename, charset, check_charset_mode="strict"):
        """ read internal data file in memory as unicode."""
        filehandler = self.opendata(filename, "r", charset, check_charset_mode)
        content = filehandler.read()
        filehandler.close()
        return content

    def opendata_bin(self, filename, mode):
        """ open internal data file as binary."""
        if "w" in mode:
            dirshouldbethere(os.path.dirname(filename))
        return open(filename, mode)

    def readdata_bin(self, filename):
        """ read internal data file in memory as binary."""
        filehandler = self.opendata_bin(filename, mode="rb")
        content = filehandler.read()
        filehandler.close()
        return content
