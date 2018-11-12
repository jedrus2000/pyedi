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

