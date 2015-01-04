# coding: utf-8
#
# xiaoyu <xiaokong1937@gmail.com>
#
# 2014/12/24 Merry Christmas
#
"""
Tests for xlink SDK.

"""
import unittest

from xlink import XlinkClient


class XlinkTestCase(unittest.TestCase):
    def setUp(self):
        APIKEY = '727c554409d5fa166860008db6385987782d5728'
        APIUSER = 'apiuser'
        self.client = XlinkClient(APIKEY, APIUSER)

    def test_get_cmd(self):
        self.assertEqual(self.client.sensor.get(id=4).commands[0].cmd, u'on')

if __name__ == "__main__":
    unittest.main()
