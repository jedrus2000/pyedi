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
try:
    from xml.etree import cElementTree as ET
except ImportError:
    from xml.etree import ElementTree as ET

try:
    import elementtree.ElementInclude as ETI
except ImportError:
    from xml.etree import ElementInclude as ETI

from collections import OrderedDict

from .json import Json


class JsonNoCheck(Json):
    def _node2json(self, node_instance):
        """ recursive method.
        """
        # newjsonobject is the json object assembled in the function.
        # init newjsonobject with record fields from node; sorted
        newjsonobject = OrderedDict(sorted(node_instance.record.items()))
        for (
                childnode
        ) in (
                node_instance.children
        ):  # fill newjsonobject with the lex_records from childnodes.
            key = childnode.record["BOTSID"]
            if key in newjsonobject:
                newjsonobject[key].append(self._node2json(childnode))
            else:
                newjsonobject[key] = [self._node2json(childnode)]
        del newjsonobject["BOTSID"]
        del newjsonobject["BOTSIDnr"]
        return newjsonobject

