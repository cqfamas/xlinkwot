===============
Xlink
===============
Xlink is a `Web of things` (also called `Internet of things`) backend app for a
django server. It provides RESTful APIs for your device.

Quick start
------------

1.In your settings.py, enable admin and add `xlink` and `tastypie` to your INSTALLED_APPS::

    INSTALLED_APPS = (
        ... 
        'django.contrib.admin',
        'xlink',
        'tastypie',
    )

2. Execute `python manage.py syncdb` to create table for xlink app.

3. Enable `admin` and add `xlink api` to your root urls. In your urls.py, add::

    from tastypie.api import Api

    from xlink.api.resources import (DataPointResource,
                                     UserResource,
                                     SensorResource,
                                     DeviceResource,
                                     CommandResource)


    admin.autodiscover()


    v1_api = Api(api_name='v1')
    v1_api.register(UserResource())
    v1_api.register(DataPointResource())
    v1_api.register(SensorResource())
    v1_api.register(DeviceResource())
    v1_api.register(CommandResource())


    # APIs
    urlpatterns += patterns(
        "",
        url('^api/', include(v1_api.urls)),
    )

4. Create Apikey for your user. In your django manage shell::

    >>> from tastypie.models import ApiKey
    >>> from django.contrib.auth.models import User
    >>> apiuser = User.objects.get(pk=1)
    >>> apikey = ApiKey.objects.create(user=apiuser)
    >>> apikey.save()
    >>> apikey
    <ApiKey: f20dab087bcf9ede8fc57a188f615d6763cd5cf0 for apiuser>

5. Start the debug server, add a device , a sensor and a command for that
   sensor.
6. Visit http://127.0.0.1:8000/api/v1/device/?format=json&username=apiuser&api_key=f20dab087bcf9ede8fc57a188f615d6763cd5cf0 to see the json data of your device, andvisit http://127.0.0.1:8000/api/v1/sensor/?format=json&username=apiuser&api_key=f20dab087bcf9ede8fc57a188f615d6763cd5cf0 to see the json data of your sensor, including the command for the sensor. Enjoy!

Requirements
--------------
django-tastypie

Developed and mantained by Xiao Yu.
Please feel free to report bugs and your suggestions at `here <https://github.com/xkong/xlinkwot/issues>`_.
