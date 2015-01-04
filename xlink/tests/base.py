"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from django.contrib.auth.models import User

from tastypie.test import ResourceTestCase
from tastypie.models import ApiKey


class BaseTest(ResourceTestCase):
    fixtures = ['test_xlink.xml']

    def setUp(self):
        super(BaseTest, self).setUp()

        self.username = 'apiuser'
        self.user = User.objects.get(username=self.username)
        self.api_key, created = ApiKey.objects.get_or_create(user=self.user)
        self.init()

    def init(self):
        self.model = self.get_model()
        self.model_name = self.model.__name__.lower()
        self.base_url = '/api/v1/%s/' % self.model_name
        self.detail_object = self.get_detail_object()
        self.detail_url = '/api/v1/%s/%s/' % (
            self.model_name,
            self.detail_object.pk)
        self.post_data = self.get_post_data()

        self.expected_objects_count = 3
        self.expected_list_objects_count = 2
        self.expected_object = {
            u'id': self.detail_object.pk,
            u"date_created": u"2014-11-30T20:24:15",
            u"date_modified": u"2014-11-30T20:44:19",
            u"history_time": u"2014-11-30T20:24:13",
            u"resource_uri": u"/api/v1/datapoint/2/",
            u"sensor": u"/api/v1/sensor/2/",
            u"value": u"111",
            u"user": u"/api/v1/user/%s/" % self.user.pk
        }
        self.expected_keys = [
            u'date_created', u'date_modified', u'history_time',
            u'value', u'id', u'sensor', u'resource_uri', u'user']
        self.tested_field = 'value'
        self.tested_value = u'98'
        self.expected_value = self.expected_object[self.tested_field]

    def get_model(self):
        raise NotImplementedError

    def get_detail_object(self):
        raise NotImplementedError

    def get_post_data(self):
        raise NotImplementedError

    def get_credentials(self):
        return self.create_apikey(self.username, self.api_key.key)

    def test_get_list_unauthorized(self):
        self.assertHttpUnauthorized(
            self.api_client.get(self.base_url, format='json'))

    def test_get_list_json(self):
        resp = self.api_client.get(self.base_url, format='json',
                                   authentication=self.get_credentials())
        self.assertValidJSONResponse(resp)
        self.assertEqual(len(self.deserialize(resp)['objects']),
                         self.expected_list_objects_count)
        self.assertEqual(self.deserialize(resp)['objects'][0],
                         self.expected_object)

    def test_get_list_xml(self):
        resp = self.api_client.get(self.base_url, format='xml',
                                   authentication=self.get_credentials())
        self.assertValidXMLResponse(resp)

    def test_get_detail_json(self):
        resp = self.api_client.get(self.detail_url, format='json',
                                   authentication=self.get_credentials())
        self.assertValidJSONResponse(resp)
        self.assertKeys(self.deserialize(resp), self.expected_keys)
        self.assertEqual(self.deserialize(resp)[self.tested_field],
                         self.expected_value)

    def test_get_detail_xml(self):
        resp = self.api_client.get(self.detail_url, format='xml',
                                   authentication=self.get_credentials())
        self.assertValidXMLResponse(resp)

    def test_post_list_unautheticated(self):
        self.assertHttpUnauthorized(
            self.api_client.post(self.base_url, format='json',
                                 data=self.post_data))

    def test_post_list(self):
        self.assertEqual(self.model.objects.count(),
                         self.expected_objects_count)
        self.assertHttpCreated(
            self.api_client.post(self.base_url, format='json',
                                 data=self.post_data,
                                 authentication=self.get_credentials()))
        self.assertEqual(self.model.objects.count(),
                         self.expected_objects_count + 1)

    def test_put_detail_unauthenticated(self):
        self.assertHttpUnauthorized(
            self.api_client.put(self.detail_url, format='json', data={}))

    def test_put_detail(self):
        original_data = self.deserialize(
            self.api_client.get(self.detail_url, format='json',
                                authentication=self.get_credentials()))
        new_data = original_data.copy()
        new_data[self.tested_field] = self.tested_value
        self.assertEqual(self.model.objects.count(),
                         self.expected_objects_count)
        self.assertHttpAccepted(
            self.api_client.put(self.detail_url, format='json',
                                data=new_data,
                                authentication=self.get_credentials()))
        self.assertEqual(self.model.objects.count(),
                         self.expected_objects_count)
        self.assertEqual(self.model.objects.get(
            pk=self.detail_object.pk).__dict__[self.tested_field],
            self.tested_value)

    def test_delete_detail_unauthenticated(self):
        self.assertHttpUnauthorized(
            self.api_client.delete(self.detail_url, format='json'))

    def test_delete_detail(self):
        self.assertEqual(self.model.objects.count(),
                         self.expected_objects_count)
        self.assertHttpAccepted(
            self.api_client.delete(self.detail_url, format='json',
                                   authentication=self.get_credentials()))
        self.assertEqual(self.model.objects.count(),
                         self.expected_objects_count - 1)
