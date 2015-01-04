# coding: utf-8
"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from xlink.models import DataPoint, Sensor, Device
from .base import BaseTest


class DataPointTest(BaseTest):

    def get_model(self):
        return DataPoint

    def get_detail_object(self):
        return self.model.objects.get(pk=2)

    def get_post_data(self):
        post_data = {
            'user': '/api/v1/user/{0}/'.format(self.user.pk),
            'sensor': '/api/v1/sensor/2/',
            'value': 99,
            'history_time': '2012-05-01T22:05:12',
        }
        return post_data


class SensorTest(BaseTest):

    def get_model(self):
        return Sensor

    def get_detail_object(self):
        return self.model.objects.get(pk=2)

    def get_post_data(self):
        post_data = {
            'user': '/api/v1/user/{0}/'.format(self.user.pk),
            'device': '/api/v1/device/2/',
            'tipe': 'switch',
            'title': 'test_title',
            'description': 'test all',
            'unit': '',
        }
        return post_data

    def init(self):
        super(SensorTest, self).init()
        self.expected_objects_count = 2
        self.expected_list_objects_count = 1
        self.expected_object = {
            u'id': self.detail_object.pk,
            u'user': u'/api/v1/user/%s/' % self.user.pk,
            u"description": u"温度计",
            u"device": u"/api/v1/device/2/",
            u"resource_uri": u"/api/v1/sensor/2/",
            u"tipe": u"temp sensor",
            u"title": u"温度计",
            u"unit": u"C",
        }
        self.expected_keys = self.expected_object.keys()
        self.tested_field = 'title'
        self.tested_value = u'faketitle'
        self.expected_value = self.expected_object[self.tested_field]


class DeviceTest(BaseTest):
    def get_model(self):
        return Device

    def get_detail_object(self):
        return self.model.objects.get(pk=2)

    def get_post_data(self):
        post_data = {
            u"description": u"apiuser device2",
            u"public": True,
            u"title": u"测试设备apiuser2",
            u"user": u"/api/v1/user/{0}/".format(self.user.pk)
        }
        return post_data

    def init(self):
        super(DeviceTest, self).init()
        self.expected_objects_count = 2
        self.expected_list_objects_count = 1
        self.expected_object = {
            u"description": u"apiuser device",
            u"id": self.detail_object.pk,
            u"public": True,
            u"resource_uri": u"/api/v1/device/2/",
            u"title": u"测试设备apiuser",
            u"user": u"/api/v1/user/%s/" % self.user.pk
        }
        self.expected_keys = self.expected_object.keys()
        self.tested_field = 'title'
        self.tested_value = u'faketitle'
        self.expected_value = self.expected_object[self.tested_field]
