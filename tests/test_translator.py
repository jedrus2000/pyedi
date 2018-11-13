import sys
import unittest
import logging

from pyedi.botslib.consts import *

from pyedi.botslib import (
    logger,
    config
)

from pyedi.translator import _translate_one_file


class TestTranslator(unittest.TestCase):
    def setUp(self):
        config.set(['settings','debug'], True)
        logger.addHandler(logging.StreamHandler(sys.stdout))
        logger.setLevel("DEBUG")

    def test_translate_one_file(self):
        row = {'testindicator': u'',
               'charset': u'',
               'messagetype': u'x12',
               'filename': '/big/Customers/ja/pyedi/pyedi_translator/tests/resources/x12/nb38fd80_corrected.edi',
               'fromchannel': u'att_in_our_server',
               'frompartner': u'',
               'topartner': u'',
               'editype': u'x12',
               'alt': u'',
               'idta': 158,
               'filesize': 3664,
               'frommail': None,
               'tomail': None,
               # additional fields as temporary DB mock
               'tscript': '811_4010_2_xml'
        }


        routedict = {'frompartner_tochannel_id': None,
                     'testindicator': u'',
                     'idroute': u'invoice_to_ATT',
                     'seq': 1,
                     'translateind': 1,
                     'tochannel': u'invoice_out_ATT',
                     'frommessagetype': u'x12',
                     'command': 'new',
                     'defer': False,
                     'topartner_tochannel_id': None,
                     'fromchannel': u'att_in_our_server',
                     'zip_incoming': None,
                     'frompartner': None,
                     'topartner': None,
                     'toeditype': u'xml',
                     'zip_outgoing': None,
                     'alt': u'',
                     'fromeditype': u'x12',
                     'tomessagetype': u'811_xml',
                     }


        endstatus = TRANSLATED #  330
        userscript = None
        scriptname = None

        _translate_one_file(row, routedict, endstatus, userscript, scriptname)
