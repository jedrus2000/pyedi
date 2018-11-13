from gettext import gettext as _

try:
    from xml.etree import cElementTree as ET
except ImportError:
    from xml.etree import ElementTree as ET

try:
    import elementtree.ElementInclude as ETI
except ImportError:
    from xml.etree import ElementInclude as ETI

from pyedi.botslib import (
    botsbaseimport,
    abspath,
    opendata_bin,
    OutMessageError,
    txtexc,
    logger,
)

from .outmessage import OutMessage


class TemplateHtml(OutMessage):
    """ uses Genshi library for templating. Genshi is very similar to Kid, and is the fork/follow-up of Kid.
        Kid is not being developed further; in time Kid will not be in repositories etc.
        Templates for Genshi are like Kid templates. Changes:
        - other namespace: xmlns:py="http://genshi.edgewall.org/" instead of xmlns:py="http://purl.org/kid/ns#"
        - enveloping is different: <xi:include href="${message}" /> instead of <div py:replace="document(message)"/>
        2 modes:
        1. use self.data, a class that can contain any python object (older way of working)
        2. use structure, recordedefs, write node tree. This is more like normal way of working; output is checked etc.
            the procided template can handle msot things, change only css of envelope.
    """

    class TemplateData(object):
        pass

    def __init__(self, ta_info):
        try:
            self.template = botsbaseimport("genshi.template")
        except ImportError:
            raise ImportError(
                _(
                    'Dependency failure: editype "templatehtml" requires python library "genshi".'
                )
            )
        super(TemplateHtml, self).__init__(ta_info)
        self.data = (
            TemplateHtml.TemplateData()
        )  # self.data can be used by mappingscript as container for content

    def _write(self, node_instance):
        templatefile = abspath(self.__class__.__name__, self.ta_info["template"])
        try:
            logger.debug('Start writing to file "%(filename)s".', self.ta_info)
            loader = self.template.TemplateLoader(auto_reload=False)
            tmpl = loader.load(templatefile)
        except:
            txt = txtexc()
            raise OutMessageError(
                _('While templating "%(editype)s.%(messagetype)s", error:\n%(txt)s'),
                {
                    "editype": self.ta_info["editype"],
                    "messagetype": self.ta_info["messagetype"],
                    "txt": txt,
                },
            )
        try:
            filehandler = opendata_bin(self.ta_info["filename"], "wb")
            if self.ta_info["has_structure"]:  # new way of working
                if self.ta_info["print_as_row"]:
                    node_instance.collectlines(self.ta_info["print_as_row"])
                stream = tmpl.generate(node=node_instance)
            else:
                stream = tmpl.generate(data=self.data)
            stream.render(
                method="xhtml", encoding=self.ta_info["charset"], out=filehandler
            )
        except:
            txt = txtexc()
            raise OutMessageError(
                _('While templating "%(editype)s.%(messagetype)s", error:\n%(txt)s'),
                {
                    "editype": self.ta_info["editype"],
                    "messagetype": self.ta_info["messagetype"],
                    "txt": txt,
                },
            )
        finally:
            filehandler.close()
            logger.debug(_('End writing to file "%(filename)s".'), self.ta_info)

    def writeall(self):
        if not self.root.record:
            self.root.record = {
                "BOTSID": "dummy"
            }  # dummy, is not used but needed for writeall of base class
        super(TemplateHtml, self).writeall()

