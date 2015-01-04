# coding: utf-8
#
# xiaoyu <xiaokong1937@gmail.com>
#
# 2014/11/29
#
"""
Admin for xlink app.

"""
from django.contrib import admin

from xlink.models import Sensor, Device, DataPoint, Command


class BaseUserObjectAdmin(admin.ModelAdmin):
    """
    Filte user object by request.user.
    Add user to form instance.
    """
    def queryset(self, request):
        """ Get queryset for user or all queryset for su """
        qs = super(BaseUserObjectAdmin, self).queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user, is_valid=True)

    def save_form(self, request, form, change):
        """ Save form for request.user """
        form.instance.user = request.user
        return super(BaseUserObjectAdmin, self).save_form(request, form,
                                                          change)


class DeviceAdmin(BaseUserObjectAdmin):
    fields = ('title', 'description', 'public')
    list_display = ('user', 'title', 'description', 'public')


class SensorAdmin(BaseUserObjectAdmin):
    fields = ('device', 'tipe', 'title', 'description', 'unit')
    list_display = ('id', 'user', 'title', 'device', 'tipe',
                    'description', 'unit')

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if db_field.name == 'device':
            kwargs["queryset"] = Device.objects.filter(user=request.user)
        return super(SensorAdmin, self).formfield_for_foreignkey(
            db_field, request, **kwargs)


class DataPointAdmin(BaseUserObjectAdmin):
    fields = ('sensor', 'value', 'history_time')
    list_display = ('user', 'sensor', 'value', 'history_time')

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if db_field.name == 'sensor':
            kwargs["queryset"] = Sensor.objects.filter(user=request.user)
        return super(DataPointAdmin, self).formfield_for_foreignkey(
            db_field, request, **kwargs)


class CommandAdmin(BaseUserObjectAdmin):
    fields = ('sensor', 'cmd', 'exp_date')
    list_display = ('user', 'sensor', 'cmd', 'exp_date')

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if db_field.name == 'sensor':
            kwargs["queryset"] = Sensor.objects.filter(user=request.user)
        return super(CommandAdmin, self).formfield_for_foreignkey(
            db_field, request, **kwargs)


admin.site.register(Sensor, SensorAdmin)
admin.site.register(Device, DeviceAdmin)
admin.site.register(DataPoint, DataPointAdmin)
admin.site.register(Command, CommandAdmin)
