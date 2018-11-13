import json as simplejson

from gettext import gettext as _

try:
    from xml.etree import cElementTree as ET
except ImportError:
    from xml.etree import ElementTree as ET

try:
    import elementtree.ElementInclude as ETI
except ImportError:
    from xml.etree import ElementInclude as ETI

from collections import OrderedDict

from pyedi.botslib.consts import *

from .outmessage import OutMessage


class Json(OutMessage):
    def _initwrite(self):
        super(Json, self)._initwrite()
        if self.multiplewrite:
            self._outstream.write("[")

    def _write(self, node_instance):
        """ convert node tree to appropriate python object.
            python objects are written to json by simplejson.
        """
        if self.nrmessagewritten:
            self._outstream.write(",")
        jsonobject = {node_instance.record["BOTSID"]: self._node2json(node_instance)}
        if self.ta_info["indented"]:
            indent = 2
        else:
            indent = None
        simplejson.dump(
            jsonobject,
            self._outstream,
            skipkeys=False,
            ensure_ascii=False,
            check_circular=False,
            indent=indent,
        )

    def _closewrite(self):
        if self.multiplewrite:
            self._outstream.write("]")
        super(Json, self)._closewrite()

    def _node2json(self, node_instance):
        """ recursive method.
        """
        # newjsonobject is the json object assembled in the function.
        newjsonobject = (
            node_instance.record.copy()
        )  # init newjsonobject with record fields from node
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
        try:
            del newjsonobject["BOTSIDnr"]
        except:
            pass
        return newjsonobject

    def _node2jsonold(self, node_instance):
        """ recursive method.
        """
        newdict = node_instance.record.copy()
        if node_instance.children:  # if this node has records in it.
            sortedchildren = {}  # empty dict
            for childnode in node_instance.children:
                botsid = childnode.record["BOTSID"]
                if botsid in sortedchildren:
                    sortedchildren[botsid].append(self._node2json(childnode))
                else:
                    sortedchildren[botsid] = [self._node2json(childnode)]
            for key, value in sortedchildren.items():
                if len(value) == 1:
                    newdict[key] = value[0]
                else:
                    newdict[key] = value
        del newdict["BOTSID"]
        return newdict

    def _canonicalfields(self, node_instance, record_definition):
        """ subclassed method; sorts using OrderedDict
            For all fields: check M/C, format.
            Fields are sorted according to grammar.
            Fields are never added.
        """
        noderecord = node_instance.record
        new_noderecord = OrderedDict()
        for field_definition in record_definition[
            FIELDS
        ]:  # loop over fields in grammar
            value = noderecord.get(field_definition[ID])
            if not value:
                if field_definition[MANDATORY]:
                    self.add2errorlist(
                        _(
                            '[F02]%(linpos)s: Record "%(mpath)s" field "%(field)s" is mandatory.\n'
                        )
                        % {
                            "linpos": node_instance.linpos(),
                            "mpath": self.mpathformat(record_definition[MPATH]),
                            "field": field_definition[ID],
                        }
                    )
                if value is None:  # None-values are not used
                    continue
            new_noderecord[field_definition[ID]] = self._formatfield(
                value, field_definition, record_definition, node_instance
            )
        node_instance.record = new_noderecord

