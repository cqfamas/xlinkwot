一、概述
---------
本文主要探讨一种使用Django作为物联网服务器，由OpenWrt设备和Arduino单片机共同组成硬件设备的物联网解决方案。

- Django是python语言的一种Web框架，通过Django可以快速搭建Web应用服务程序。
- OpenWrt是一个嵌入式linux的发行版。OpenWrt设备则是安装了这个发型版系统的设备（通常是路由器设备）。
- Arduino是一款基于AVR的单片机，它提供了自己的编程APIs和硬件。

本文所述的物联网解决方案，实际上由Django提供物联网服务，由OpenWrt和Arduino共同构成Arduino Yun系统。用户执行命令的流程是：用户登录到Django服务器，设置Arduino设备要执行的命令，Arduino设备通过OpenWrt设备获取要执行的命令，Arduino设备执行命令。
不同于OpenWrt驱动Arduino的方案，本方案采用的是Arduino Yun的解决方案，Arduino与OpenWrt之间通过TTL线连接Rx，Tx接口。通过OpenWrt的USB口连接Arduino的USB口实现供电和数据交换。

 *严格来说，Django只是一个Web框架，本文为了行文方便，将「基于Django的Web服务器及其应用程序」统称为Django服务器。*

（一）硬件方案
+++++++++++++++

1.一个支持Django的服务器
~~~~~~~~~~~~~~~~~~~~~~~~~~
本文为了方便部署，节约硬件成本，使用的是Sina提供的SAE云平台。
实际生产环境下，可以选择自己搭建服务器，或使用其他PaSS服务等。

2.一个支持OpenWrt的硬件设备（CPU:AR9331，16M以上Flash）
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
基于与Arduino组合为Arduino Yun的思路考虑，本文选用的是TPLINK
TL-703N系列（及其马甲系列，水星、迅捷），通过改装Flash为16M实现。
实际生产环境中，可以使用基于AR9331核心的路由器设备。

3.Arduino单片机设备
~~~~~~~~~~~~~~~~~~~~~
基于与OpenWrt构成Arduino Yun的思路，本文选用的是Arduino Mega 2560。

4.替代方案
~~~~~~~~~~~~~~~~

 - 上述的2+3可以直接使用Arduino Yun设备。
 - 上述的3可以使用其他控制器，相应的实现代码也需要进行修改。
 - 上述的2可以使用其他服务器设备，只需要支持互联网访问、支持python，能支持配套的控制板即可。

（二）控制流
+++++++++++++++++

- 由Django提供基础物联网服务，各种设备通过与Django服务器沟通，获取指令执行，或者上传指令，上传数据。
- 由OpenWrt提供指令中转服务，同时将Django返回的指令翻译给Arduino。
- 由Arduino控制各类传感器执行。

二、基于Django的物联网服务端的实现
------------------------------------
基于Django的服务端，用来作为物联网服务器。用户可以通过移动设备等访问Django服务器，获取Arduino设备上各类传感器的数据，向Arduino发送指令等。

（一）数据方案
++++++++++++++++
基于各种原因，我们采用了RESTful APIs的数据模式。由Django提供RESTful
APIs，供上下游设备使用。
Django实现RESTful APIs有很多插件，本文使用的是 `tastypie
<http://tastypieapi.org/>`_
。Django-tastypie提供了5种认证方法（Basic，ApiKey，Session，Digest,
OAuth），出于Arduino及OpenWrt的实际需要，我们选择的认证方法是ApiKey方法。即，硬件设备（OpenWrt、Arduino）和上游设备（上位机：PC, 移动设备等）采用向服务器发送ApiKey和ApiUsername的方式实现认证。
 **注意**
 *事实上，采用这种ApiKey的认证方法是存在安全风险的，因此不建议在互联网中使用这种认证。它不能有效避免中间人攻击。如果有条件，建议使用OAuth2.0进行认证（Django-tastypie也可以实现OAuth2.0认证）。*

数据格式上，我们选择的是json，虽然选择xml和选择json对于服务端和客户端来说技术难度上区别不是很大，但是我们依然决定使用json。当然，默认也提供xml格式的数据。

（二）数据模型（Model）与数据管理
++++++++++++++++++++++++++++++++++
主要的数据模型有User，Device，Sensor，DataPoint, Command。

- User：用户及用户权限控制等等，使用的是Django默认的User模型。
- Device：用户设备，一个设备可以有很多传感器。比如Arduino及OpenWrt可以作为一个用户设备。
- Sensor: 设备传感器，一个设备上可以有多个传感器。比如Arduino上连接的各种温度传感器。注意，开关也算做传感器的一种。
- DataPoint：数据点。由传感器取得的数据，经Arduino和OpenWrt上传至此。
- Command： 命令。用户在Django上设置此命令，Arduino通过OpenWrt获取此命令执行。

以下是Model部分的源代码（初步框架，生产环境请酌情修改，为了行文方便，只针对最简单的情况）:

.. code-block:: python

    # coding: utf-8
    #
    # xiaoyu <xiaokong1937#gmail.com>
    #
    # 2014/10/14
    #
    """
    Models for xlink.

    """
    from django.db import models
    from django.contrib.auth.models import User
    from django.utils.translation import ugettext_lazy as _


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


    class Device(models.Model):
        user = models.ForeignKey(User)
        title = models.CharField(verbose_name=_('title'), max_length=32)
        description = models.TextField(_('description'), blank=True)
        public = models.BooleanField(_('show to public'), default=False)
        is_valid = models.BooleanField(_('Valid', default=True))

        def __unicode__(self):
            return self.title

        class Meta:
            verbose_name = _('device')
            verbose_name_plural = _('devices')


    class Sensor(models.Model):
        user = models.ForeignKey(User)
        device = models.ForeignKey(Device)
        tipe = models.CharField(_('sensor type'), max_length=64,
                                choices=SENSOR_CHOICES)
        title = models.CharField(verbose_name=_('title'), max_length=32)
        description = models.TextField(_('description'), blank=True)
        #  TODO: validate unit in forms
        unit = models.CharField(_('unit'), blank=True, choices=UNIT_CHOICES,
                                max_length=32)
        is_valid = models.BooleanField(_('Valid', default=True))


        def __unicode__(self):
            return self.title

        class Meta:
            verbose_name = _("sensor")
            verbose_name_plural = _("sensors")

        def save(self, *args, **kwargs):
            if self.user != self.device.user:
                return
            #  Validate unit and type.
            #  FIXME: sensor and unit filte.
            if self.unit:
                #  Validate Temperature Sensor
                if self.tipe == 'temp sensor' and self.unit not in ['C', 'F']:
                    self.unit = 'C'
                #  Validate  Switch
                if self.tipe == 'switch':
                    self.unit = ''
            return super(Sensor, self).save(*args, **kwargs)


    class DataPoint(models.Model):
        user = models.ForeignKey(User)
        sensor = models.ForeignKey(Sensor)
        value = models.CharField(_('value'), max_length=256)
        history_time = models.DateTimeField(verbose_name=_("time happened"),
                                            blank=True, null=True)
        is_valid = models.BooleanField(_('Valid', default=True))

        class Meta:
            verbose_name = _("datapoint")
            verbose_name_plural = _("datapoints")

        def save(self, *args, **kwargs):
            if self.user != self.sensor.user:
                return
            return super(DataPoint, self).save(*args, **kwargs)


    class Command(models.Model):
        # TODO: use composit primary key (sensor & cmd), as unique cmd to a sensor.
        user = models.ForeignKey(User)
        sensor = models.ForeignKey(Sensor, unique=True)
        cmd = models.CharField(_('command'), max_length=64)
        exp_time = models.DateTimeField(verbose_name=_('expire time'),
                                        blank=True, null=True)
        is_valid = models.BooleanField(_('Valid', default=True))

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

以上是Model部分的示例，因为比较简单，所以不展开解释。其中还有许多地方可以优化，比如整个数据模型也可以不这么设计。或者不使用Django的ORM，而使用NoSQL数据库（针对此项目，优势不明显）。

当然模型设计好之后，最简单的办法就是增加admin.py使得用户能够通过Django Admin进行管理。你也可以自己写一个更好的管理方案。[1]_

.. [1] 为什么这时候不直接采用RESTful APIs来实现管理呢？答：此时使用RESTful APIs来进行管理是可行的。但是为了有一个直观的认识，以及测试OpenWrt能否正常工作等，暂时先使用Django默认的Admin进行数据管理。

以下是admin.py的部分源码：

.. code-block:: python

    # coding: utf-8
    #
    # xiaoyu <xiaokong1937#gmail.com>
    #
    # 2014/11/29
    #
    """
    Admin for xlink app.

    """
    from django.contrib import admin
    from django import forms
    from django.utils.translation import ugettext_lazy as _

    from xlink.models import Sensor, Device, DataPoint, Command
    from utils.admin_utils import BaseUserObjectAdmin
    from utils.mixin import DateTimePickerMixin


    class DataPointForm(forms.ModelForm):
        history_time = forms.DateTimeField(
            widget=forms.TextInput(
                attrs={'onmousedown': "pickme()", 'id': 'id_previous_t'}),
            help_text=_('Click to select time.'),
            label=_('Record time.'))

        class Meta:
            model = DataPoint
            fields = ('sensor', 'value', 'history_time')


    class CommandForm(forms.ModelForm):
        exp_date = forms.DateTimeField(
            widget=forms.TextInput(
                attrs={'onmousedown': "pickme()", 'id': 'id_previous_t'}),
            help_text=_('Click to select time.'),
            label=_('expire time.'))

        class Meta:
            model = Command
            fields = ('sensor', 'cmd', 'exp_date')


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


    class DataPointAdmin(DateTimePickerMixin, BaseUserObjectAdmin):
        fields = ('sensor', 'value', 'history_time')
        list_display = ('user', 'sensor', 'value', 'history_time')
        form = DataPointForm

        def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
            if db_field.name == 'sensor':
                kwargs["queryset"] = Sensor.objects.filter(user=request.user)
            return super(DataPointAdmin, self).formfield_for_foreignkey(
                db_field, request, **kwargs)


    class CommandAdmin(DateTimePickerMixin, BaseUserObjectAdmin):
        fields = ('sensor', 'cmd', 'exp_date')
        list_display = ('user', 'sensor', 'cmd', 'exp_date')
        form = CommandForm

        def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
            if db_field.name == 'sensor':
                kwargs["queryset"] = Sensor.objects.filter(user=request.user)
            return super(CommandAdmin, self).formfield_for_foreignkey(
                db_field, request, **kwargs)


    admin.site.register(Sensor, SensorAdmin)
    admin.site.register(Device, DeviceAdmin)
    admin.site.register(DataPoint, DataPointAdmin)
    admin.site.register(Command, CommandAdmin)

其中，DateTimePickerMixin，BaseUserObjectAdmin是两个自定义的class，实现的功能是时间选择，和对用户进行权限控制（用户只能操作自己的对象）。
当然，上面这个实例也有很多地方可以继续优化。

后续的内容将会介绍如何使用Django和django-tastypie实现RESTful APIs以及在硬件上的各种实现。

（三）RESTful APIs的实现
++++++++++++++++++++++++++

如前文所述，我们采用的是django-tastypie实现Django的RESTful APIs支持。

下面对django-tastypie来个一分钟简介。基本上，你需要使用django的Model（其实不是必须的，因为tastypie也支持NoSQL），然后写个api.py，在其中引入你的Model，继承Resource类，然后在你的urls.py中，将这个Resource实例化，之后在urlpatterns之中加入Resource的url pattern。然后访问该API对应的url，比如http://127.0.0.1:8000/api/entry/。

官方的示例如下：

.. code-block:: python

    # myapp/api.py
    from tastypie.resources import ModelResource
    from myapp.models import Entry


    class EntryResource(ModelResource):
        class Meta:
            queryset = Entry.objects.all()
            resource_name = 'entry'

    # urls.py
    from django.conf.urls.defaults import *
    from myapp.api import EntryResource

    entry_resource = EntryResource()

    urlpatterns = patterns('',
        # The normal jazz here...
        (r'^blog/', include('myapp.urls')),
        (r'^api/', include(entry_resource.urls)),
    )

当然，在我们实际的生产环境中，要实现的东西远比这个复杂。比如需要实现用户的权限控制，包括用户是否有权限登录到Django服务器，用户是否有权限操作当前资源，当前资源中的某些字段用户是否有权限接触到等等。再比如，要实现Django Model之间的relationship，比如一对一、一对多、多对多关系等等。

以下逐步分析源码，进行讲解。

.. code-block:: python

    from tastypie import fields
    from tastypie.resources import ModelResource, ALL_WITH_RELATIONS
    from tastypie.authentication import ApiKeyAuthentication

    from xlink.models import DataPoint, Sensor, Device, Command
    from ninan.api import UserResource
    from utils.authorization import UserObjectsOnlyAuthorization


    class DeviceResource(ModelResource):
        user = fields.ForeignKey(UserResource, 'user')

        class Meta:
            queryset = Device.objects.filter(is_valid=True, is_private=False)
            allowed_methods = ['get', 'put', 'post', 'delete']
            authentication = ApiKeyAuthentication()
            authorization = UserObjectsOnlyAuthorization()
            fields = ['id', 'title', 'description', 'public']
            filtering = {
                'user': ALL_WITH_RELATIONS,
            }

注意上面这些代码，与实例相比，增加了一行
  **user = fields.ForeignKey(UserResource, 'user')**
这一行的作用是把已经写好的UserResource作为一个外键引用到当前的Resource并以user字段存在。UserResource是我在另一个文件中写好的东西。主要实现获取用户的username等信息。读者可以自己实现。

源码中 **Meta** 部分：

- *queryset* 基本同Django的queryset，就是对Model做一个过滤，过滤出需要给用户看的数据。
- *allowed_methods* 即为允许使用的方法，这里允许GET,PUT,POST,DELETE四种方法。
- *authentication* 鉴权方法，即鉴证是否为合法的用户。这里使用的是tastypie的ApiKeyAuthentication。
- *authorization* 授权方法，即验证用户是否有必要的权限操作数据。这里使用的是自己实现的UserObjectsOnlyAuthorization，顾名思义，就是用户只有权限操作创建人为该用户的数据。
- *fields* 显示给用户的字段。
- *filtering* 是否支持对某一字段进行过滤。

基本上，以上这个Resource实现了将Device这个Model扩展为RESTful APIs。可以将以上这些代码保存为apis.py，放在，比如xlink这个app下面。这样xlink这个app中可能的文件结构是

- xlink

  - __init__.py
  - apis.py
  - models.py
  - admin.py
  - views.py
  - urls.py

然后在你的项目的urls.py中，增加

.. code-block:: python

    from tastypie.api import Api

    from xlink.apis import DeviceResource
    
    v1_api = Api(api_name='v1')
    v1_api.register(DeviceResource())
     

    # APIs
    urlpatterns = patterns(
        "",
        url('^api/', include(v1_api.urls)),

    )

这样访问http://127.0.0.1:8080/api/v1/device/?format=json&username=apiuser&api_key=your_api_key 就应该可以看到你的device信息了。

然后关于SensorResource的实现也跟DeviceResource差不多，不过Senor在实现的时候要兼顾CommandResource，因为我可以直接访问某个Sensor而直接获取ta的Command。当然其实也可以直接在Model设计的时候就把Command设置为Sensor的一个field，之所以没有这么做，是考虑以后可能会对Command进行管控，设置成Sensor的一个field不利于这么实现。
下面是SensorResource的代码。重申一下，这些只是为了行文方便而单独拿出来的代码片段，可能不能直接运行。完整的代码我会看情况在github上开源。

.. code-block:: python

    class SensorResource(ModelResource):
        device = fields.ForeignKey(DeviceResource, 'device')
        user = fields.ForeignKey(UserResource, 'user')
        commands = fields.ToManyField('xlink.api.resources.CommandResource',
                                      'command_set',
                                      full=True)

        class Meta:
            queryset = Sensor.objects.filter(is_valid=True, is_private=False)
            allowed_methods = ['get', 'put', 'post', 'delete']
            authentication = ApiKeyAuthentication()
            authorization = UserObjectsOnlyAuthorization()
            fields = ['id', 'tipe', 'title', 'description', 'unit']
            filtering = {
                'device': ALL_WITH_RELATIONS,
                'user': ALL_WITH_RELATIONS,
                'cmd': ALL_WITH_RELATIONS
            }

上面的代码相比之前的几个Resource，增加的地方主要是这里
    **commands = fields.ToManyField('xlink.api.resources.CommandResource',** 
                                  **'command_set',** 
                                  **full=True)** 

这个fields.ToManyField实际上可以将两个在Django的Model中关联不大甚至没有关联的Model通过这个形式组合起来，使得通过Sensor可以直接访问其Command。注意ToManyField的三个参数，第一个'xlink.api.resources.CommandResouce'是用来指定关联的Resource的位置的，文档中说了，即便跟现有的SensorResource在一个py文件里，也要用这种类似绝对路径的方式来写。第二个'command_set'看着很熟悉对不对，像不像Django Model中关于relation的字段？（User.object_set.all()这样）。文档中说这个东西叫什么名字不重要，但其实是重要的，因为如果ta叫foo_bar的话，访问SensorResource会提示Sensor.foo_bar不是一个有效的Sensor field。那么我们想想就明白了，这个必须得是Sensor的一个字段名。那么我们可以直接用Django的relation字段，xx_set。这样对应从SensorResource访问CommandResource就会变成类似Sensor.command_set.xxx这样。

其实到这里，最关键的Model的RESTful APIs已经实现了。说白了我要用Arduino获取的就是一个关于当前设备的一个命令。比如可以在Arduino里编程实现，当获取的命令是`on`的时候，我打开pin 13的LED之类之类。

Arduino端只要指定每隔多长时间定时通过API获取这个设备的指令，然后执行就可以了。而这个指令的设定，完全可以通过移动端登录Django admin来修改、可以通过开放的APIs通过其他设备修改等等等等。比如我可能想远程查看自己家里的温度，那就可以给Arduino加装一个Temperature Sensor，温度传感器。然后通过登录Django admin修改这个Sensor的指令为get之类的，然后Arduino发送温度传感器获取的室温，传给Django服务器或者什么的。


三、OpenWrt提供的后端服务
------------------------------------

在现有的技术方案中，有一个是通过Arduino连接互联网扩展板，通过Arduino直接与物联网服务器进行沟通，获取服务器指令。我们不对这个方案做更多的评价。我个人更倾向于，让OpenWrt来处理获取并解析物联网服务器指令的工作，因为OpenWrt上可以装python啊，有了python这个强大的工具，实现OAuth2.0认证也不是问题（其实是有点问题的，不过可以绕过）。包括获取物联网服务器json数据之后的解析工作，用python来做总好过用Arduino来做吧。

另外一点就是，如果将来不使用Arduino而使用其他控制板的话，OpenWrt这边几乎不需要做改动，只需要其他控制板做一些小的调整就行了。本质上是，控制板给OpenWrt发送信号，执行某命令A，A这个命令则执行xx.py，xx.py再与Django服务器通信。

所以基于以上的种种，我们决定让OpenWrt承担与Django服务器直接通信、获取服务器返回的json数据，解析等等工作。

（一）RESTful APIs的python SDK
++++++++++++++++++++++++++++++++

首先要做的就是给Django实现的RESTful APIs写个SDK。没有SDK的REST不是好REST。这里其实实现难度也不大，可以参照一些开源SDK的实现，进而改为自己的SDK。当然，实际应用中要注意这些SDK的协议。

这里我们采用的是经过修改后的 `sinaweibopy <https://github.com/michaelliao/sinaweibopy>`_
,主要参考了其中的sns.py，但是使用了requests替代了原有的urllib。其实自己实现一个也比较简单。所以这里不放源码了。还是那句话，这一系列的文章写完之后，会视情况将源码放出。乃至本文的rst源文件（嗯，LaTeX改吧改吧就能当论文用）。

（二）OpenWrt端的命令行工具
+++++++++++++++++++++++++++++

这个命令行工具我们暂时叫做xlink。执行的时候直接::

    root@openwrt# xlink subcommand arg1 arg2 --option1 ....

我们设置这个命令行工具的目的，是让Arduino通过Process模块，执行这个xlink命令，进而与Django通信。注意xlink命令是放在OpenWrt上的，Arduino只是调用这个命令而已。

关于xlink命令的实现模式上，我们参照的是Django的manage.py的实现模式。同时因为原来manage.py有些功能我们用不到，实际中做了精简。考虑到Django的是基于BSD协议发布的，这里我们会将这部分代码进行开源。

以下是xlink的代码，其实这是一个py文件，为了调用方便，直接存为xlink，然后链接到OpenWrt的/usr/bin

.. code-block:: python

    #!/usr/bin/env python
    # coding: utf-8
    #
    # xiaoyu <xiaokong1937#gmail.com>
    #
    # 2014/12/24
    #
    # xlink
    """
    Process Backend for xlink-arduino.
    Note: some of the codes taken from Django source.

    E.g( Arduino yun):
      Process p;
      p.begin("xlink");
      p.addParameter("get_sensor_cmd");
      p.addParameter("-k");
      p.addParameter(APIKEY);
      p.addParameter("-u");
      p.addParameter(APIUSER);
      p.addParameter("-s");
      p.addParameter(SENSORID);
      p.run();
      

     """
    import sys
    import os
    from importlib import import_module
    from optparse import NO_DEFAULT, OptionParser

    from base import BaseCommand, logger

    _commands = None
    current_path = os.path.dirname(os.path.realpath(__file__))
    sys.path.insert(0, current_path)


    class CommandError(Exception):
        pass


    def find_commands(command_path):
        command_dir = os.path.join(command_path, 'commands')
        try:
            return [f[:-3] for f in os.listdir(command_dir)
                    if not f.startswith('_') and f.endswith('.py')]
        except OSError:
            return []


    def get_commands():
        global _commands
        if _commands is None:
            _commands = [name for name in find_commands(current_path)]
        return _commands


    def load_command_class(name):
        """
        Given a command name, returns the Command class instance.

        All errors raised by the import process (ImportError, AttributeError)
        are allowed to propagete.

        """
        module = import_module('commands.{}'.format(name))
        return module.Command()


    def call_command(name, *args, **options):
        """
        Call the given command, with the given options and args/kwargs.

        This is the primary API you should use for calling specific commands.

        Some examples:
            call_command('syncdb')
            call_command('shell', plain=True)
            call_command('sqlall', 'myapp')
        """
        if name not in get_commands():
            raise CommandError('Not a valid command.')
        # Load the command object.
        klass = load_command_class(name)
        defaults = {}
        for opt in klass.option_list:
            if opt.default is NO_DEFAULT:
                defaults[opt.dest] = None
            else:
                defaults[opt.dest] = opt.default
        defaults.update(options)

        return klass.execute(*args, **defaults)


    class LaxOptionParser(OptionParser):
        def error(self, msg):
            pass

        def print_help(self):
            pass

        def print_lax_help(self):
            OptionParser.print_help(self)

        def _process_args(self, largs, rargs, values):
            while rargs:
                arg = rargs[0]
                try:
                    if arg[0:2] == "--" and len(arg) > 2:
                        self._process_long_opt(rargs, values)
                    elif arg[:1] == "-" and len(arg) > 1:
                        self._process_short_opts(rargs, values)
                    else:
                        del rargs[0]
                        raise Exception
                except:
                    largs.append(arg)


    class ManagementUtility(object):
        def __init__(self, argv=None):
            self.argv = argv or sys.argv[:]
            self.prog_name = os.path.basename(self.argv[0])

        def fetch_command(self, subcommand):
            if subcommand not in get_commands():
                raise CommandError('Not a valid command.')
            # Load the command object.
            klass = load_command_class(subcommand)
            return klass

        def execute(self):
            parser = LaxOptionParser(usage="%prog subcommand [options] [args]",
                                     version='1.0.0',
                                     option_list=BaseCommand.option_list)
            options, args = parser.parse_args(self.argv)
            try:
                subcommand = self.argv[1]
            except IndexError:
                subcommand = 'help'
            if subcommand == 'help':
                parser.print_help()
                return
            self.fetch_command(subcommand).run_from_argv(self.argv)


    def execute_from_command_line(argv=None):
        utility = ManagementUtility(argv)
        logger.debug("Cmd called with argv [{}]".format(str(argv)))
        utility.execute()


    if __name__ == "__main__":
        execute_from_command_line(sys.argv)

基本上跟Django的management的实现方式一样。而且还支持扩展。只需要将命令写成py文件放在xlink同级目录的commands文件夹下就可以调用执行了。
完整的代码会视情况在github上开源。

下面是获取sensor指令的实现。get_sensor_cmd.py:

.. code-block:: python

    #!/usr/bin/env python
    # coding: utf-8
    #
    # xiaoyu <xiaokong1937#gmail.com>
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
            # TODO: Handle exceptions
            apikey = options.get('apikey')
            apiuser = options.get('apiuser')
            sensorid = options.get('sensorid')
            c = XlinkClient(apikey, apiuser)
            r = c.sensor.get(id=sensorid)
            cmd = r.commands[0].cmd
            logger.debug("Cmd got : {}".format(cmd))
            print cmd

关于以上代码的几个解释：
    from xlink_sdk.xlink import XlinkClient
这里的xlink_sdk即为上文提到的RESTful APIs的python SDK。

    from base import BaseCommand, logger

这里的base.py里实现了BaseCommand类。同时也实现了logging。
最后exceute的时候，我们只需要把结果打印出来就可以了。因为Arduino是通过Process模块
获取命令的执行结果的。

四、 Arduino端的实现
----------------------

Arduino端实现的东西比较简单，就是定期执行OpenWrt上的xlink
get_sensor_cmd命令，获取Django服务器上为当前sensor设置的命令即可。

xlink_blink.ino::

    // Xlink examples
    //
    // xiaoyu <xiaokong1937#gmail.com>
    //
    // 2014/12/26
    // 
    #include <Bridge.h>
    #include <String.h>
    #include <Process.h>

    // Xlink apis
    #define APIKEY "727c554409d5fa16008db6385987782d5728" // Apikey of Xlink 
    #define APIUSER "apiuser" // Username of Xlink 
    #define SENSORID "4" // Sensor ID
    #define DEFAULT_CMD "off" // Default command used for execCommand
    // String that store the current command.
    String command;

    void setup() {
      // Bridge takes about two seconds to start up
      // it can be helpful to use the on-board LED
      // as an indicator for when it has initialized

      pinMode(13, OUTPUT);
      pinMode(12, OUTPUT);
      digitalWrite(13, LOW);

      Bridge.begin();
      digitalWrite(13, HIGH);

      Console.begin();

      while (!Console); // wait for a serial connection
      Console.println("Console ready.");
    }

    void loop() {
      digitalWrite(12, LOW);
      // Get command from xlink server.
      command = getCommand();
      Console.print(command);
      // Execute the command.
      execCommand(command);
      delay(3000);
    }

    String getCommand() {
      Process p;
      String cmd="";
      p.begin("xlink");
      p.addParameter("get_sensor_cmd");
      p.addParameter("-k");
      p.addParameter(APIKEY);
      p.addParameter("-u");
      p.addParameter(APIUSER);
      p.addParameter("-s");
      p.addParameter(SENSORID);
      p.run();
      
      while (p.available()>0) {
        char c = p.read();
        Console.print(int(c));
        cmd.concat(c);
      }
      cmd.trim();
      if (cmd == ""){
        return DEFAULT_CMD;
      }
      return cmd;
    }

    void execCommand(String command){
      if (command == "on" ){
        digitalWrite(12, HIGH);
      }else{
        digitalWrite(13, LOW);
      };
    }

将以上的代码修改后写入Arduino，连上OpenWrt，即可每3秒获取Django服务器为4号传感器设置的命令，并且执行。

五、总结
-----------

以上只是实现了通过Django为物联网提供服务器服务，使用OpenWrt + Arduino（或者直接使用Arduino
Yun设备），点亮LED的功能。本文旨在介绍一种实现方法，完整的代码请参考后期放出的github仓库地址。
