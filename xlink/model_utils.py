#!/usr/bin/env python
# coding: utf-8
#
# xiaoyu <xiaokong1937@gmail.com>
#
# 2014/04/01
#
# Code taken with permission from Carl Meyer's very useful django-model-utils
#
# From <Two Scoops of Django - Best Practices For Django 1.5>
#
"""
Model utils for ninan project.
"""
from django.db import models
from django.utils.timezone import now, localtime
from django.utils.translation import ugettext_lazy as _


class AutoCreatedField(models.DateTimeField):
    """
    A DateTimeField that automatically populates itself at
    object creation.

    By default, sets editable=False, default=now

    """
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('editable', False)
        kwargs.setdefault('default', now)
        super(AutoCreatedField, self).__init__(*args, **kwargs)


class AutoLastModifiedField(AutoCreatedField):
    """
    A DateTimeField that updates itself on each save() of the model.

    By default, sets editable=False and default=now

    """
    def pre_save(self, model_instance, add):
        value = now()
        setattr(model_instance, self.attname, value)
        return value


class TimeStampedModel(models.Model):
    """
    An abstract base class model that provides self-updating
    ``created`` and ``modified`` fields.

    """
    date_created = AutoCreatedField(_('created'))
    date_modified = AutoLastModifiedField(_('modified'))
    is_valid = models.BooleanField(_('is_valid'), default=True)
    is_private = models.BooleanField(_('is_private'))

    class Meta:
        abstract = True

    def natural_key(self):
        return self.id

    def display_date(self):
        return localtime(self.date_created)
    display_date.short_description = _('Created Time')
