import json as simplejson
from gettext import gettext as _

from pyedi.botslib.consts import *
from pyedi.botslib import (
    InMessageError,
)
import pyedi.node as node
from .inmessage import InMessage


class Json(InMessage):
    def initfromfile(self):
        self.messagegrammarread(typeofgrammarfile="grammars")
        self._readcontent_edifile()

        jsonobject = simplejson.loads(self.rawinput)
        del self.rawinput
        if isinstance(jsonobject, list):
            self.root = node.Node()  # initialise empty node.
            self.root.children = self._dojsonlist(
                jsonobject, self._getrootid()
            )  # fill root with children
            for child in self.root.children:
                if not child.record:  # sanity test: the children must have content
                    raise InMessageError(_("[J51]: No usable content."))
                self.checkmessage(child, self.defmessage)
                self.ta_info.update(child.queries)
        elif isinstance(jsonobject, dict):
            if len(jsonobject) == 1 and isinstance(list(jsonobject.values())[0], dict):
                # best structure: {rootid:{id2:<dict, list>}}
                self.root = self._dojsonobject(
                    list(jsonobject.values())[0], list(jsonobject.keys())[0]
                )
            elif len(jsonobject) == 1 and isinstance(
                    list(jsonobject.values())[0], list
            ):
                # root dict has no name; use value from grammar for rootID; {id2:<dict, list>}
                self.root = node.Node(
                    record={"BOTSID": self._getrootid()}
                )  # initialise empty node.
                self.root.children = self._dojsonlist(
                    list(jsonobject.values())[0], list(jsonobject.keys())[0]
                )
            else:
                self.root = self._dojsonobject(jsonobject, self._getrootid())
            if not self.root:
                raise InMessageError(_("[J52]: No usable content."))
            self.checkmessage(self.root, self.defmessage)
            self.ta_info.update(self.root.queries)
        else:
            # root in JSON is neither dict or list.
            raise InMessageError(_('[J53]: Content must be a "list" or "object".'))

    def _getrootid(self):
        return self.defmessage.structure[0][ID]

    def _dojsonlist(self, jsonobject, name):
        lijst = (
            []
        )  # initialise empty list, used to append a listof (converted) json objects
        for i in jsonobject:
            if isinstance(i, dict):  # check list item is dict/object
                newnode = self._dojsonobject(i, name)
                if newnode:
                    lijst.append(newnode)
            elif self.ta_info["checkunknownentities"]:
                raise InMessageError(_('[J54]: List content must be a "object".'))
        return lijst

    def _dojsonobject(self, jsonobject, name):
        thisnode = node.Node(record={"BOTSID": name})  # initialise empty node.
        for key, value in jsonobject.items():
            if value is None:
                continue
            elif isinstance(value, str):  # json field; map to field in node.record
                ## for generating grammars: empty strings should generate a field
                if value and not value.isspace():  # use only if string has a value.
                    thisnode.record[key] = value
            elif isinstance(value, dict):
                newnode = self._dojsonobject(value, key)
                if newnode:
                    thisnode.append(newnode)
            elif isinstance(value, list):
                thisnode.children.extend(self._dojsonlist(value, key))
            elif isinstance(
                    value, (int, float)
            ):  # json field; map to field in node.record
                thisnode.record[key] = str(value)
            else:
                if self.ta_info["checkunknownentities"]:
                    raise InMessageError(
                        _(
                            '[J55]: Key "%(key)s" value "%(value)s": is not string, list or dict.'
                        ),
                        {"key": key, "value": value},
                    )
                thisnode.record[key] = str(value)
        if len(thisnode.record) == 2 and not thisnode.children:
            return None  # node is empty...
        # ~ thisnode.record['BOTSID']=name
        return thisnode

