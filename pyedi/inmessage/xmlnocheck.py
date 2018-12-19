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
from .xml import Xml


class XmlNoCheck(Xml):
    """ class for ediobjects in XML. Uses ElementTree"""

    def checkmessage(self, node_instance, defmessage, subtranslation=False):
        pass

    def _entitytype(self, xmlchildnode):
        if len(xmlchildnode):
            self.stack.append(0)
            return 1
        return 0

    def stackinit(self):
        self.stack = [0]  # stack to track where we are in stucture of grammar

