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

