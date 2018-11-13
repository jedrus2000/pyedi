try:
    from xml.etree import cElementTree as ET
except ImportError:
    from xml.etree import ElementTree as ET

try:
    import elementtree.ElementInclude as ETI
except ImportError:
    from xml.etree import ElementInclude as ETI

from .xml import Xml


class XmlNoCheck(Xml):
    def _node2xmlfields(self, noderecord):
        """ write record as xml-record-entity plus xml-field-entities within the xml-record-entity.
            output is sorted alfabetically, attributes alfabetically.
        """
        recordtag = noderecord.pop("BOTSID")
        del noderecord["BOTSIDnr"]
        BOTSCONTENT = noderecord.pop("BOTSCONTENT", None)
        # ***collect from noderecord all entities and attributes***************************
        attributemarker = self.ta_info["attributemarker"]
        attributedict = {}  # is a dict of dicts
        for key, value in noderecord.items():
            if attributemarker in key:
                field, attribute = key.split(attributemarker, 1)
                if not field in attributedict:
                    attributedict[field] = {}
                attributedict[field][attribute] = value
            else:
                if not key in attributedict:
                    attributedict[key] = {}
        # ***generate the xml-record-entity***************************
        xmlrecord = ET.Element(
            recordtag, attributedict.pop(recordtag, {})
        )  # pop from attributedict->do not use later
        # ***add BOTSCONTENT as the content of the xml-record-entity
        xmlrecord.text = BOTSCONTENT
        # ***generate the xml-field-entities within the xml-record-entity***************************
        for key in sorted(attributedict.keys()):  # sorted: predictable output
            ET.SubElement(xmlrecord, key, attributedict[key]).text = noderecord.get(key)
        return xmlrecord


