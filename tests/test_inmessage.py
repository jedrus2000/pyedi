import sys
import unittest
import logging

from pyedi.inmessage import parse_edi_file
from pyedi.botslib.logger import logger


class TestInMessage(unittest.TestCase):
    def setUp(self):
        logger.addHandler(logging.StreamHandler(sys.stdout))
        logger.setLevel("DEBUG")

    def test_parse_edi_file(self):
        ta_info = {
            'testindicator': '',
            'idroute': 'invoice_to_ATT',
            'charset': '',
            'messagetype': 'x12',
            'filename': '/big/Customers/ja/pyedi/pyedi_translator/tests/resources/x12/nb38fd80_corrected.edi',
            'fromchannel': u'att_in_our_server',
            'command': 'new',
            'frompartner': '',
            'topartner': '',
            'editype': 'x12',
            'alt': ''
        }
        edi_object = parse_edi_file(**ta_info)
        print(*edi_object.errorlist)
        #  edi_object.checkforerrorlist()

