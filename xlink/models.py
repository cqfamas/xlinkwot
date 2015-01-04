# coding: utf-8
#
# xiaoyu <xiaokong1937@gmail.com>
#
# 2014/10/14
#
"""
Models for xlink.

"""
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from model_utils import TimeStampedModel


SENSOR_CHOICES = (
    ('switch', _('Switch')),
    ('temp sensor', _('Temperature Sensor'))
)


UNIT_CHOICES = (
    ('C', _('degree Celsius')),
    ('F', _('degree Fahrenheit')),
    ('m', _('meter')),
    ('null', _('on or off')),
)


class Device(TimeStampedModel):
    user = models.ForeignKey(User)
    title = models.CharField(verbose_name=_('title'), max_length=32)
    description = models.TextField(_('description'), blank=True)
    public = models.BooleanField(_('show to public'), default=False)

    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = _('device')
        verbose_name_plural = _('devices')


class Sensor(TimeStampedModel):
    user = models.ForeignKey(User)
    device = models.ForeignKey(Device)
    tipe = models.CharField(_('sensor type'), max_length=64,
                            choices=SENSOR_CHOICES)
    title = models.CharField(verbose_name=_('title'), max_length=32)
    description = models.TextField(_('description'), blank=True)
#  TODO: validate unit in forms
    unit = models.CharField(_('unit'), blank=True, choices=UNIT_CHOICES,
                            max_length=32)

    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = _("sensor")
        verbose_name_plural = _("sensors")

    def save(self, *args, **kwargs):
        if self.user != self.device.user:
            return
        #  Validate unit and type.
        if self.unit:
            #  Validate Temperature Sensor
            if self.tipe == 'temp sensor' and self.unit not in ['C', 'F']:
                self.unit = 'C'
            #  Validate  Switch
            if self.tipe == 'switch':
                self.unit = ''
        return super(Sensor, self).save(*args, **kwargs)


class DataPoint(TimeStampedModel):
    user = models.ForeignKey(User)
    sensor = models.ForeignKey(Sensor)
    value = models.CharField(_('value'), max_length=256)
    history_time = models.DateTimeField(verbose_name=_("time happened"),
                                        blank=True, null=True)

    class Meta:
        verbose_name = _("datapoint")
        verbose_name_plural = _("datapoints")

    def save(self, *args, **kwargs):
        if self.user != self.sensor.user:
            return
        return super(DataPoint, self).save(*args, **kwargs)


class Command(TimeStampedModel):
    # TODO: use composit primary key (sensor & cmd), as unique cmd to a sensor.
    user = models.ForeignKey(User)
    sensor = models.ForeignKey(Sensor, unique=True)
    cmd = models.CharField(_('command'), max_length=64)
    exp_date = models.DateTimeField(verbose_name=_('expire time'),
                                    blank=True, null=True)

    class Meta:
        verbose_name = _("command")
        verbose_name_plural = _("commands")

    def __unicode__(self):
        return '%s_%s' % (self.sensor, self.cmd)

    def save(self, *args, **kwargs):
        # FIXME: maybe very slow with huge data.
        if self.user != self.sensor.user:
            return
        commands = Command.objects.filter(sensor=self.sensor, user=self.user)
        commands = commands.values('cmd')
        unique_cmds = [cmdz['cmd'] for cmdz in commands]
        if self.cmd in unique_cmds:
            return
        return super(Command, self).save(*args, **kwargs)
