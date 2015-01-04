#!/usr/bin/env python
# coding: utf-8
#
# xiaoyu <xiaokong1937@gmail.com>
#
# 2014/12/25
#
"""
Get sensor command from xlink server.

Usage:
    xlink get_sensor_cmd -k your_api_key -u your_username -s sensor_id

"""
from optparse import make_option

from xlink_sdk.xlink import XlinkClient
from base import BaseCommand, logger


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-k', '--apikey', action='store', dest='apikey',
                    default='', help='APIKEY of xlink.'),
        make_option('-u', '--apiuser', action='store', dest='apiuser',
                    default='', help='APIUSER of xlink.'),
        make_option('-s', '--sensorid', action='store', dest='sensorid',
                    default='', help='Sensor ID of xlink.'),
    )

    def execute(self, *args, **options):
        apikey = options.get('apikey')
        apiuser = options.get('apiuser')
        sensorid = options.get('sensorid')
        c = XlinkClient(apikey, apiuser)
        r = c.sensor.get(id=sensorid)
        cmd = r.commands[0].cmd
        logger.debug("Cmd got : {}".format(cmd))
        print cmd
