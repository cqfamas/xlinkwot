#!/usr/bin/env python
# coding: utf-8
#
# xiaoyu <xiaokong1937@gmail.com>
#
# 2014/05/08
#
"""
Authorizations for tastypie.

"""
from tastypie.authorization import DjangoAuthorization
from tastypie.exceptions import Unauthorized


class UserObjectsAuthorization(DjangoAuthorization):
    """
    A user only being able to access or modify "their" objects.
    For ready, a user can get all objects.
    """

    def create_list(self, object_list, bundle):
        return self.update_list(object_list, bundle)

    def create_detail(self, object_list, bundle):
        return bundle.obj.user == bundle.request.user

    def update_list(self, object_list, bundle):
        allowed = []

        for obj in object_list:
            if obj.user == bundle.request.user:
                allowed.append(obj)

        return allowed

    def update_detail(self, object_list, bundle):
        return bundle.obj.user == bundle.request.user

    def delete_list(self, object_list, bundle):
        raise Unauthorized("Sorry, no deletes")

    def delete_detail(self, object_list, bundle):
        raise Unauthorized("Sorry, no deletes")


class UserOnlyAuthorization(DjangoAuthorization):

    def read_list(self, object_list, bundle):
        return self.update_list(object_list, bundle)

    def read_detail(self, object_list, bundle):
        return bundle.obj == bundle.request.user

    def create_list(self, object_list, bundle):
        raise Unauthorized("Sorry, no deletes")

    def create_detail(self, object_list, bundle):
        raise Unauthorized("Sorry, no deletes")

    def update_list(self, object_list, bundle):
        allowed = []

        for obj in object_list:
            if obj == bundle.request.user:
                allowed.append(obj)

        return allowed

    def update_detail(self, object_list, bundle):
        return bundle.obj == bundle.request.user

    def delete_list(self, object_list, bundle):
        raise Unauthorized("Sorry, no deletes")

    def delete_detail(self, object_list, bundle):
        raise Unauthorized("Sorry, no deletes")


class UserObjectsOnlyAuthorization(UserOnlyAuthorization):
    def read_list(self, object_list, bundle):
        # This assumes a ``QuerySet`` from ``ModelResource``.
        return object_list.filter(user=bundle.request.user)

    def read_detail(self, object_list, bundle):
        # Is the requested object owned by the user?
        return bundle.obj.user == bundle.request.user

    def create_list(self, object_list, bundle):
        return object_list

    def create_detail(self, object_list, bundle):
        return bundle.obj.user == bundle.request.user

    def update_list(self, object_list, bundle):
        allowed = []

        # Since they may not all be saved, iterate over them.
        for obj in object_list:
            if obj.user == bundle.request.user:
                allowed.append(obj)

        return allowed

    def update_detail(self, object_list, bundle):
        return bundle.obj.user == bundle.request.user

    def delete_list(self, object_list, bundle):
        allowed = []

        # Since they may not all be saved, iterate over them.
        for obj in object_list:
            if obj.user == bundle.request.user:
                allowed.append(obj)
        return allowed

    def delete_detail(self, object_list, bundle):
        return bundle.obj.user == bundle.request.user
