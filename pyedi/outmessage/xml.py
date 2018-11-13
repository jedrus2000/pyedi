import sys

try:
    from xml.etree import cElementTree as ET
except ImportError:
    from xml.etree import ElementTree as ET

try:
    import elementtree.ElementInclude as ETI
except ImportError:
    from xml.etree import ElementInclude as ETI


from pyedi.botslib.consts import *
from pyedi.botslib import (
    indent_xml,
    opendata_bin,
    logger,
)

from .outmessage import OutMessage


class Xml(OutMessage):
    """ Some problems with right xml prolog, standalone, DOCTYPE, processing instructons: Different ET versions give different results.
        Things work OK for python 2.7
        celementtree in 2.7 is version 1.0.6, but different implementation in 2.6??
        For python <2.7: do not generate standalone, DOCTYPE, processing instructions for encoding !=utf-8,ascii OR if elementtree package is installed (version 1.3.0 or bigger)
    """

    def _write(self, node_instance):
        """ write normal XML messages (no envelope)"""
        xmltree = ET.ElementTree(self._node2xml(node_instance))
        root = xmltree.getroot()
        self._xmlcorewrite(xmltree, root)

    def envelopewrite(self, node_instance):
        """ write envelope for XML messages"""
        self._initwrite()
        self.checkmessage(node_instance, self.defmessage)
        self.checkforerrorlist()
        xmltree = ET.ElementTree(self._node2xml(node_instance))
        root = xmltree.getroot()
        ETI.include(root)
        self._xmlcorewrite(xmltree, root)
        self._closewrite()

    def _xmlcorewrite(self, xmltree, root):
        if sys.version_info[0] == 2 and sys.version_info[1] == 6:
            python26 = True
        else:
            python26 = False
        if (
                not python26 and self.ta_info["namespace_prefixes"]
        ):  # Register any namespace prefixes specified in syntax
            for eachns in self.ta_info["namespace_prefixes"]:
                ET.register_namespace(eachns[0], eachns[1])
        # xml prolog: always use.*********************************
        # standalone, DOCTYPE, processing instructions: only possible in python >= 2.7 or if encoding is utf-8/ascii
        if (
                not python26
                or self.ta_info["charset"] in ["us-ascii", "utf-8"]
                or ET.VERSION >= "1.3.0"
        ):
            if self.ta_info["indented"]:
                indentstring = b"\n"
            else:
                indentstring = b""
            if self.ta_info["standalone"]:
                standalonestring = 'standalone="%s" ' % (self.ta_info["standalone"])
            else:
                standalonestring = ""
            processing_instruction = ET.ProcessingInstruction(
                "xml",
                'version="%s" encoding="%s" %s'
                % (self.ta_info["version"], self.ta_info["charset"], standalonestring),
                )
            # do not use encoding here. gives double xml prolog; possibly because
            # ET.ElementTree.write i used again by write()
            self._outstream.write(ET.tostring(processing_instruction) + indentstring)
            # doctype /DTD **************************************
            if self.ta_info["DOCTYPE"]:
                # ~ self._outstream.write(b'<!DOCTYPE %s>'%(self.ta_info['DOCTYPE']) + indentstring)
                self._outstream.write(
                    b"<!DOCTYPE "
                    + self.ta_info["DOCTYPE"].encode("ascii")
                    + b">"
                    + indentstring
                )
            # processing instructions (other than prolog) ************
            if self.ta_info["processing_instructions"]:
                for eachpi in self.ta_info["processing_instructions"]:
                    processing_instruction = ET.ProcessingInstruction(
                        eachpi[0], eachpi[1]
                    )
                    # do not use encoding here. gives double xml prolog; possibly because
                    # ET.ElementTree.write i used again by write()
                    self._outstream.write(
                        ET.tostring(processing_instruction) + indentstring
                    )
        # indent the xml elements
        if self.ta_info["indented"]:
            indent_xml(root)
        # write tree to file; this is different for different python/elementtree versions
        if python26 and ET.VERSION < "1.3.0":
            xmltree.write(self._outstream, encoding=self.ta_info["charset"])
        else:
            xmltree.write(
                self._outstream, encoding=self.ta_info["charset"], xml_declaration=False
            )

    def _node2xml(self, node_instance):
        """ recursive method.
        """
        newnode = self._node2xmlfields(node_instance.record)
        for childnode in node_instance.children:
            newnode.append(self._node2xml(childnode))
        return newnode

    def _node2xmlfields(self, noderecord):
        """ write record as xml-record-entity plus xml-field-entities within the xml-record-entity.
            output is sorted according to grammar, attributes alfabetically.
        """
        recordtag = noderecord.pop("BOTSID")
        del noderecord["BOTSIDnr"]
        BOTSCONTENT = noderecord.pop("BOTSCONTENT", None)
        # collect all values used as attributes from noderecord***************************
        attributemarker = self.ta_info["attributemarker"]
        attributedict = {}  # is a dict of dicts
        for key, value in noderecord.items():
            if attributemarker in key:
                field, attribute = key.split(attributemarker, 1)
                if not field in attributedict:
                    attributedict[field] = {}
                attributedict[field][attribute] = value
                # ~ del noderecord[key]
        # generate xml-record-entity***************************
        xmlrecord = ET.Element(recordtag, attributedict.get(recordtag, {}))
        # ***add BOTSCONTENT as the content of the xml-record-entity
        xmlrecord.text = BOTSCONTENT
        # generate the xml-field-entities within the xml-record-entity***************************
        # loop over remaining fields in 'record': write these as subelements
        for field_def in self.defmessage.recorddefs[recordtag]:
            if (
                    attributemarker in field_def[ID]
            ):  # skip fields that are marked as xml attributes
                continue
            content = noderecord.get(field_def[ID], None)
            attributes = attributedict.get(field_def[ID], {})
            if content is not None or attributes:
                ET.SubElement(
                    xmlrecord, field_def[ID], attributes
                ).text = content  # add xml element to xml record
        return xmlrecord

    def _initwrite(self):
        logger.debug('Start writing to file "%(filename)s".', self.ta_info)
        self._outstream = opendata_bin(self.ta_info["filename"], "wb")

