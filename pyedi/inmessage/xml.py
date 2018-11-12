try:
    from xml.etree import cElementTree as ET
except ImportError:
    from xml.etree import ElementTree as ET

from gettext import gettext as _

# bots-modules

from pyedi.botslib.consts import *
from pyedi.botslib import (
    abspathdata,
    InMessageError,
    BotsImportError,
    botsimport,
    logger,
)
import pyedi.node as node

from .inmessage import InMessage


class Xml(InMessage):
    """ class for ediobjects in XML. Uses ElementTree"""

    def initfromfile(self):
        logger.debug('Read edi file "%(filename)s".', self.ta_info)
        filename = abspathdata(self.ta_info["filename"])

        if self.ta_info["messagetype"] == "mailbag":
            # the messagetype is not know.
            # bots reads file usersys/grammars/xml/mailbag.py, and uses 'mailbagsearch' to determine the messagetype
            # mailbagsearch is a list, containing python dicts. Dict consist of 'xpath', 'messagetype' and (optionally) 'content'.
            # 'xpath' is a xpath to use on xml-file (using elementtree xpath functionality)
            # if found, and 'content' in the dict; if 'content' is equal to value found by xpath-search, then set messagetype.
            # if found, and no 'content' in the dict; set messagetype.
            try:
                module, grammarname = botsimport("grammars", "xml", "mailbag")
                mailbagsearch = getattr(module, "mailbagsearch")
            except AttributeError:
                logger.error("Missing mailbagsearch in mailbag definitions for xml.")
                raise
            except BotsImportError:
                logger.error("Missing mailbag definitions for xml, should be there.")
                raise
            parser = ET.XMLParser()
            try:
                extra_character_entity = getattr(module, "extra_character_entity")
                for key, value in extra_character_entity.items():
                    parser.entity[key] = value
            except AttributeError:
                pass  # there is no extra_character_entity in the mailbag definitions, is OK.
            etree = (
                ET.ElementTree()
            )  # ElementTree: lexes, parses, makes etree; etree is quite similar to bots-node trees but conversion is needed
            etreeroot = etree.parse(filename, parser)
            for item in mailbagsearch:
                if "xpath" not in item or "messagetype" not in item:
                    raise InMessageError(_("Invalid search parameters in xml mailbag."))
                found = etree.find(item["xpath"])
                if found is not None:
                    if "content" in item and found.text != item["content"]:
                        continue
                    self.ta_info["messagetype"] = item["messagetype"]
                    break
            else:
                raise InMessageError(
                    _("Could not find right xml messagetype for mailbag.")
                )

            self.messagegrammarread(typeofgrammarfile="grammars")
        else:
            self.messagegrammarread(typeofgrammarfile="grammars")
            parser = ET.XMLParser()
            for key, value in self.ta_info["extra_character_entity"].items():
                parser.entity[key] = value
            etree = (
                ET.ElementTree()
            )  # ElementTree: lexes, parses, makes etree; etree is quite similar to bots-node trees but conversion is needed
            etreeroot = etree.parse(filename, parser)
        self._handle_empty(etreeroot)
        self.stackinit()
        self.root = self._etree2botstree(etreeroot)  # convert etree to bots-nodes-tree
        self.checkmessage(self.root, self.defmessage)
        self.ta_info.update(self.root.queries)

    def _handle_empty(self, xmlnode):
        if xmlnode.text:
            xmlnode.text = xmlnode.text.strip()
        for key, value in xmlnode.items():
            xmlnode.attrib[key] = value.strip()
        for xmlchildnode in xmlnode:  # for every node in mpathtree
            self._handle_empty(xmlchildnode)

    def _etree2botstree(self, xmlnode):
        """ recursive. """
        newnode = node.Node(
            record=self._etreenode2botstreenode(xmlnode)
        )  # make new node, use fields
        for xmlchildnode in xmlnode:  # for every node in mpathtree
            entitytype = self._entitytype(xmlchildnode)
            if not entitytype:  # is a field, or unknown that looks like a field
                if xmlchildnode.text:  # if xml element has content, add as field
                    newnode.record[
                        xmlchildnode.tag
                    ] = xmlchildnode.text  # add as a field
                # convert the xml-attributes of this 'xml-filed' to fields in dict with attributemarker.
                newnode.record.update(
                    (xmlchildnode.tag + self.ta_info["attributemarker"] + key, value)
                    for key, value in xmlchildnode.items()
                    if value
                )
            elif entitytype == 1:  # childnode is a record according to grammar
                # go recursive and add child (with children) as a node/record
                newnode.append(self._etree2botstree(xmlchildnode))
                self.stack.pop()  # handled the xmlnode, so remove it from the stack
            else:  # is a record, but not in grammar
                if self.ta_info["checkunknownentities"]:
                    self.add2errorlist(
                        _(
                            '[S02]%(linpos)s: Unknown xml-tag "%(recordunkown)s" (within "%(record)s") in message.\n'
                        )
                        % {
                            "linpos": newnode.linpos(),
                            "recordunkown": xmlchildnode.tag,
                            "record": newnode.record["BOTSID"],
                        }
                    )
                continue
        return newnode  # return the new node

    def _etreenode2botstreenode(self, xmlnode):
        """ build a basic dict from xml-node. Add BOTSID, xml-attributes (of 'record'), xmlnode.text as BOTSCONTENT."""
        build = dict(
            (xmlnode.tag + self.ta_info["attributemarker"] + key, value)
            for key, value in xmlnode.items()
            if value
        )  # convert xml attributes to fields.
        build["BOTSID"] = xmlnode.tag
        if xmlnode.text:
            build["BOTSCONTENT"] = xmlnode.text
        return build

    def _entitytype(self, xmlchildnode):
        """ check if xmlchildnode is field (or record)"""
        structure_level = self.stack[-1]
        if LEVEL in structure_level:
            for structure_record in structure_level[
                LEVEL
            ]:  # find xmlchildnode in structure
                if xmlchildnode.tag == structure_record[ID]:
                    self.stack.append(structure_record)
                    return 1
        # tag not in structure. Check for children; Return 2 if has children
        if len(xmlchildnode):
            return 2
        return 0

    def stackinit(self):
        self.stack = [
            self.defmessage.structure[0]
        ]  # stack to track where we are in stucture of grammar

