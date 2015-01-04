#!/usr/bin/env python
# coding: utf-8
#
# xiaoyu <xiaokong1937@gmail.com>
#
# 2014/12/24 Merry Christmas!
#
"""
SDK for xlink app of Ninan Project.

"""
import json

from req import BaseRequestsClient


class JsonDict(dict):
    '''
    General json object that allows attributes to be bound
    to and also behaves like a dict.
    '''
    def __getattr__(self, attr):
        try:
            return self[attr]
        except KeyError:
            raise AttributeError(
                r"'JsonDict' object has no attribute '%s'" % attr)

    def __setattr__(self, attr, value):
        self[attr] = value


def _parse_json(s):
    '''
    Parse json string into JsonDict.

    '''
    if not s:
        return s
    return json.loads(s, object_hook=lambda pairs: JsonDict(pairs.iteritems()))


class XlinkClient(BaseRequestsClient):
    def __init__(self, apikey, apiuser, debug=True):
        self.apikey = apikey
        self.apiuser = apiuser
        self.host = "ninan.sinaapp.com" if not debug else "192.168.1.122:8080"
        super(XlinkClient, self).__init__(host=self.host)
        self._set_headers()
        self.api_url = 'http://{}/api/v1'.format(self.host)

    def _set_headers(self):
        super(XlinkClient, self)._set_headers()
        realm = "ApiKey {}:{}".format(self.apiuser, self.apikey)
        self.headers.update({"Authorization": realm})

    def __getattr__(self, attr):
        return _Callable(self, attr)

    def call_api(self, http_method, http_path, **kwargs):
        method, url, headers, params = self._prepare_api(
            http_method, http_path, **kwargs)
        #  TODO: Handle HTTP Errors
        resp = self._request(url, method, headers, params)
        if resp.status_code not in range(200, 207):
            return self.on_error("Bad request: {}".format(resp.status_code))
        try:
            resp = _parse_json(resp.content)
        except ValueError, e:
            return self.on_error(e)
        return resp

    def _prepare_api(self, http_method, http_path, **kwargs):
        if 'id' in kwargs:
            _id = kwargs.get('id')
            url = '{}/{}/{}/?format=json'.format(self.api_url, http_path, _id)
            kwargs.pop('id')
        else:
            url = '{}/{}/?format=json'.format(self.api_url, http_path)
        return http_method, url, self.headers, kwargs

    def on_error(self, reason):
        resp = {
            'xlink_error': reason
        }
        return resp


class _Executable(object):

    def __init__(self, client, method, path):
        self._client = client
        self._method = method
        self._path = path

    def __call__(self, **kw):
        return self._client.call_api(self._method, self._path, **kw)

    def __str__(self):
        return '_Executable (%s %s)' % (self._method, self._path)

    __repr__ = __str__


class _Callable(object):

    def __init__(self, client, name):
        self._client = client
        self._name = name

    def __getattr__(self, attr):
        if attr == 'get':
            return _Executable(self._client, 'GET', self._name)
        if attr == 'post':
            return _Executable(self._client, 'POST', self._name)
        name = '%s/%s' % (self._name, attr)
        return _Callable(self._client, name)

    def __str__(self):
        return '_Callable (%s)' % self._name

    __repr__ = __str__


if __name__ == "__main__":
    APIKEY = '727c55448'
    APIUSER = 'apiuser'
    c = XlinkClient(APIKEY, APIUSER)
    r = c.sensor.get(id=5)
    print r
