try:
    from xml.etree import cElementTree as ET
except ImportError:
    from xml.etree import ElementTree as ET

from gettext import gettext as _

# bots-modules

from pyedi.botslib import (
    botsbaseimport,
    abspathdata,
    txtexc,
    InMessageError,
    logger,
)
import pyedi.node as node

from .csv import Csv


class Excel(Csv):
    def initfromfile(self):
        """ initialisation from an excel file.
            file is first converted to csv using python module xlrd
        """
        try:
            self.xlrd = botsbaseimport("xlrd")
        except ImportError:
            raise ImportError(
                _('Dependency failure: editype "excel" requires python library "xlrd".')
            )
        import csv as csvlib

        try:
            import StringIO
        except:
            import io as StringIO

        self.messagegrammarread(typeofgrammarfile="grammars")
        self.ta_info["charset"] = self.defmessage.syntax[
            "charset"
        ]  # always use charset of edi file.
        if self.ta_info["escape"]:
            doublequote = False
        else:
            doublequote = True

        logger.debug('Read edi file "%(filename)s".', self.ta_info)
        # xlrd reads excel file; python's csv modules write this to file-like
        # StringIO (as utf-8); read StringIO as self.rawinput; decode this
        # (utf-8->str)
        infilename = abspathdata(self.ta_info["filename"])
        try:
            xlsdata = self.read_xls(infilename)
        except:
            txt = txtexc()
            logger.error(
                _("Excel extraction failed, may not be an Excel file? Error:\n%(txt)s"),
                {"txt": txt},
            )
            raise InMessageError(
                _("Excel extraction failed, may not be an Excel file? Error:\n%(txt)s"),
                {"txt": txt},
            )
        rawinputfile = StringIO.StringIO()
        csvout = csvlib.writer(
            rawinputfile,
            quotechar=self.ta_info["quote_char"],
            delimiter=self.ta_info["field_sep"],
            doublequote=doublequote,
            escapechar=self.ta_info["escape"],
        )
        csvout.writerows(map(self.utf8ize, xlsdata))
        rawinputfile.seek(0)
        self.rawinput = rawinputfile.read()
        rawinputfile.close()
        self.rawinput = self.rawinput.decode("utf-8")
        # start lexing and parsing as csv
        self._lex()
        if hasattr(self, "rawinput"):
            del self.rawinput
        self.root = node.Node()  # make root Node None.
        self.iternext_lex_record = iter(self.lex_records)
        leftover = self._parse(
            structure_level=self.defmessage.structure, inode=self.root
        )
        if leftover:
            raise InMessageError(
                _('[A52]: Found non-valid data at end of excel file: "%(leftover)s".'),
                {"leftover": leftover},
            )
        del self.lex_records
        self.checkmessage(self.root, self.defmessage)

    def read_xls(self, infilename):
        # Read excel first sheet into a 2-d array
        book = self.xlrd.open_workbook(infilename)
        sheet = book.sheet_by_index(0)
        formatter = lambda t, v: self.format_excelval(book, t, v, False)  # python3
        xlsdata = []
        for row in range(sheet.nrows):
            (types, values) = (sheet.row_types(row), sheet.row_values(row))
            xlsdata.append(map(formatter, zip(types, values)))
        return xlsdata

    # -------------------------------------------------------------------------------

    def format_excelval(self, book, datatype, value, wanttupledate):
        #  Convert excel data for some data types
        if datatype == 2:
            if value == int(value):
                value = int(value)
        elif datatype == 3:
            datetuple = self.xlrd.xldate_as_tuple(value, book.datemode)
            value = datetuple if wanttupledate else self.tupledate_to_isodate(datetuple)
        elif datatype == 5:
            value = self.xlrd.error_text_from_code[value]
        return value

    # -------------------------------------------------------------------------------

    def tupledate_to_isodate(self, tupledate):
        # Turns a gregorian (year, month, day, hour, minute, nearest_second) into a
        # standard YYYY-MM-DDTHH:MM:SS ISO date.
        (y, m, d, hh, mm, ss) = tupledate
        nonzero = lambda n: n != 0
        datestring = "%04d-%02d-%02d" % (y, m, d) if filter(nonzero, (y, m, d)) else ""
        timestring = (
            "T%02d:%02d:%02d" % (hh, mm, ss)
            if filter(nonzero, (hh, mm, ss)) or not datestring
            else ""
        )
        return datestring + timestring

    # -------------------------------------------------------------------------------

    def utf8ize(self, l):
        # Make string-like things into utf-8, leave other things alone
        return [str(s).encode("utf-8") if hasattr(s, "encode") else s for s in l]

