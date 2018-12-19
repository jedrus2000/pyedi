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

from pyedi.botslib import GrammarError
from .grammar import Grammar


class Xml(Grammar):
    def class_specific_tests(self):
        if not self.syntax["envelope"] and self.syntax["merge"]:
            raise GrammarError(
                _(
                    'Grammar "%(grammar)s": in this xml grammar merge is "True" but no (user) enveloping is specified. This will lead to invalid xml files'
                ),
                {"grammar": self.grammarname},
            )

    defaultsyntax = {
        "attributemarker": "__",
        "charset": "utf-8",
        "checkcharsetin": "strict",  # strict, ignore or botsreplace (replace with char as set in bots.ini).
        "checkcharsetout": "strict",  # strict, ignore or botsreplace (replace with char as set in bots.ini).
        "checkunknownentities": True,
        "contenttype": "text/xml ",
        "decimaal": ".",
        "DOCTYPE": "",  # doctype declaration to use in xml header. 'DOCTYPE': 'mydoctype SYSTEM "mydoctype.dtd"'  will lead to: <!DOCTYPE mydoctype SYSTEM "mydoctype.dtd">
        "envelope": "",
        # additional character entities to resolve when parsing XML; mostly html
        # character entities. Example:
        # {'euro':'','nbsp':unichr(160),'apos':'\u0027'}
        "extra_character_entity": {},
        "indented": False,  # False: xml output is one string (no cr/lf); True: xml output is indented/human readable
        "merge": False,
        # to over-ride default namespace prefixes (ns0, ns1 etc) for outgoing xml.
        # is a list, consisting of tuples, each tuple consists of prefix and uri.
        "namespace_prefixes": None,
        # Example: 'namespace_prefixes':[('orders','http://www.company.com/EDIOrders'),]
        # to generate processing instruction in xml prolog. is a list, consisting
        # of tuples, each tuple consists of type of instruction and text for
        # instruction.
        "processing_instructions": None,
        # Example: 'processing_instructions': [('xml-stylesheet' ,'href="mystylesheet.xsl" type="text/xml"'),('type-of-ppi' ,'attr1="value1" attr2="value2"')]
        # leads to this output in xml-file:  <?xml-stylesheet
        # href="mystylesheet.xsl" type="text/xml"?><?type-of-ppi attr1="value1"
        # attr2="value2"?>
        "standalone": None,  # as used in xml prolog; values: 'yes' , 'no' or None (not used)
        "triad": "",
        "version": "1.0",  # as used in xml prolog
        # settings needed as defaults, but not useful for this editype
        "add_crlfafterrecord_sep": "",
        "escape": "",
        "field_sep": "",
        "forcequote": 0,  # csv only
        "quote_char": "",
        "record_sep": "",
        "record_tag_sep": "",  # Tradacoms/GTDI
        "reserve": "",
        "sfield_sep": "",
        "skip_char": "",
        # bots internal, never change/overwrite
        "has_structure": True,  # is True, read structure, recorddef, check these
        "checkcollision": False,
        "lengthnumericbare": False,
        "stripfield_sep": False,
    }