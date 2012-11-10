#coding=utf-8
import xcat
import xcat.models as models
import xcat.web
import functools
import tornado.web 
from tornado.web import RequestHandler
from tornado.web import UIModule
from tornado.util import import_object 
from xcat.utils import Json , Date
from xcat import cache

'''
  基于事件的插件机制

    Request 执行流程 ：

      on_init -> before_execute -> before_render -> on_finish

'''

_application = False

# 注册 application
def register_app(application):
    global _application 
    _application = application
    init()


'''
  在工作的插件列表

  格式：

  {
    'on_init' : [
        { 'targets' : ['app.controllers.admin.*'] , 'plugin' : pluginObj , 'callback' : 'on_init' } ,
        ...
    ] ,
    'before_execute' : [
        { 'targets' : ['app.controllers.admin.*'] , 'plugin' : pluginObj , 'callback' : 'before_execute' } ,
        ...
    ] ,
    ...
  }
'''

_list = {}

# 定义更新时间
_plugins_key = ''

_cache_key = 'xcat.plugins.key'




'''
  初始化
'''
def init():
    
    # 创建表
    xcat.Database.connect(xcat.Database.READ)
    if False == models.Plugins.table_exists():
        models.Plugins.create_table()
    
    reset()
    xcat.Database.close()

'''
  重置
'''    
def reset():
    global _list , _plugins_key , _cache_key

    _work_plugins = []
    _config       = {}
    _list         = {}

    for plugin in models.Plugins.select().order_by(models.Plugins.id.desc()):
        _work_plugins.append(plugin.name)
        _config[plugin.name] = Json.decode(plugin.config)

        # 注册插件路由
        for handler in Json.decode(plugin.handlers,[]):
            import_object(handler)

        binds = Json.decode(plugin.bind,{})
        for event in binds:
            _list.setdefault(event,[])
            for v in binds[event]:
                v['handler'] = import_object(str(plugin.name))
                v['name'] = plugin.name
                _list[event].append(v)

    _plugins_key = '|'.join(_work_plugins)
    cache.client.set(_cache_key,_plugins_key)

    cache.client.set('xcat.plugins.work_plugins',_work_plugins)
    cache.client.set('xcat.plugins.config',_config)

def is_sync():
    global _plugins_key, _cache_key
    return cache.client.get(_cache_key) == _plugins_key

def get_work_names():
    return cache.client.get('xcat.plugins.work_plugins', [])

'''
  取可用插件列表
'''
def get_list():
    global _list
    return _list

'''
  取插件的配置
'''
def get_config(plugin_name,default = {}):
    _config = cache.client.get('xcat.plugins.config',{})
    return _config.get(plugin_name,default)

def set_config(plugin_name,config):
    _config = cache.client.get('xcat.plugins.config',{})
    pl_ar = models.Plugins.get(models.Plugins.name == plugin_name)
    pl_ar.config = Json.encode(config)
    pl_ar.save()
    _config[plugin_name] = config
    cache.client.set('xcat.plugins.config',_config)

'''
  调用对应的插件
'''
def call(event, that):
    target   = that.__class__.__module__ + '.' + that.__class__.__name__
    handlers = []

    for v in get_list().get(event,[]):
        if v['target'].find('*') == -1 and v['target'] == target:
            handlers.append(v)
        else:
            key = v['target'].split('*')[0]
            if target.find(key) == 0 or v['target'] == '*' :
                handlers.append(v)
    return handlers


class Events(object):
    '''
    handler 事件绑定
    '''
               
    '''
      控制器初始化时执行

        注： 这时数据库连接还未打开
    '''
    @staticmethod
    def on_init(method):

        @functools.wraps(method)
        def wrapper(self):
            # 插件不同步，执行同步
            if False == is_sync():
                xcat.Database.connect()
                reset()

            handlers = call('on_init', self)
     
            for v in handlers:
                plugin = v['handler']()
                # 设置上下文
                plugin._context = {
                    'self' : self ,
                }
                if False == getattr(plugin,v['callback'])():
                    return False
            
            return method(self)

        return wrapper

    # 控制器执行前调用
    @staticmethod
    def before_execute(method):

        @functools.wraps(method)
        def wrapper(self, transforms, *args, **kwargs):



            handlers = call('before_execute', self)
     
            for v in handlers:
                plugin = v['handler']()
                # 设置上下文
                plugin._context = {
                    'transforms' : transforms ,
                    'args'       : args ,
                    'kwargs'     : kwargs ,
                    'self'       : self
                }
           
                if False == getattr(plugin,v['callback'])():
                    return False

                transforms = plugin._context['transforms']
                args       = plugin._context['args']
                kwargs     = plugin._context['kwargs']

            return method(self, transforms, *args, **kwargs)

        return wrapper

    # 渲染模板前调用
    @staticmethod
    def before_render(method):

        @functools.wraps(method)
        def wrapper(self, template_name, **kwargs):
            handlers = call('before_render', self)
     
            for v in handlers:
                plugin = v['handler']()
                # 设置上下文
                plugin._context = {
                    'template_name' : template_name ,
                    'kwargs'        : kwargs ,
                    'self'          : self
                }
                if False == getattr(plugin,v['callback'])():
                    return False
                template_name = plugin._context['template_name']
                kwargs        = plugin._context['kwargs']
            return method(self, template_name, **kwargs)

        return wrapper

    # 完成http请求时调用
    @staticmethod
    def on_finish(method):

        @functools.wraps(method)
        def wrapper(self):
            handlers = call('on_finish', self)
     
            for v in handlers:
                plugin = v['handler']()
                # 设置上下文
                plugin._context = {
                    'self' : self ,
                }
                if False == getattr(plugin,v['callback'])():
                    return False
            return method(self)

        return wrapper

# 卸载插件
def uninstall(plugin_name):
  
    register = import_object(plugin_name.strip() + '.register')
    
    name = register._handler.__module__ + \
           '.' + register._handler.__name__

    if models.Plugins.filter(models.Plugins.name == name).count() == 1 :
        plugin = import_object(name)()
        plugin.uninstall()

        plugin_ar = models.Plugins.get(models.Plugins.name == name)

        for v in Json.decode(plugin_ar.ui_modules):
            ui_name = str(v.split('.').pop())
            if ui_name in _application.ui_modules:
                del _application.ui_modules[ui_name] 

        # 卸载路由
        routes = []

        for v in Json.decode(plugin_ar.handlers):
            ctr = import_object(v)
            if hasattr(ctr,'_menu'):
                from xcat.web import menu
                menu.remove(getattr(ctr,'_menu'))
            routes.append(ctr._route)

        if len(routes) > 0:
            # 重新注册路由
            from xcat.web import Application
            cache.client.set(Application._sync_key,Date.time())

        models.Plugins.delete().where(models.Plugins.name==name).execute()

        reset()
        #reload()


# 安装插件
def install(plugin_name):
    
    register = import_object(plugin_name.strip() + '.register')
    
    name = register._handler.__module__ + \
           '.' + register._handler.__name__


    if models.Plugins.filter(models.Plugins.name == name).count() == 0 :       
        plugin = import_object(name)()
        plugin.install()

        # 尝试自加加载 ui_modules.py
        try:
            ui_modules = import_object(plugin_name + '.uimodules')
            for v in dir(ui_modules):
                if issubclass(getattr(ui_modules,v), UIModule) \
                and v != 'UIModule':
                    plugin.add_ui_module(v)
        except Exception, e:
            pass

        # 尝试自加加载 handlers.py
        try:
            handlers = import_object(plugin_name + '.handlers')
            reload(handlers)
            for v in dir(handlers):
              
                if issubclass(getattr(handlers,v), RequestHandler) \
                and v != 'RequestHandler':

                    plugin.add_handler(v)
        except Exception, e:
            pass


        handlers = []
        for v in plugin._handlers:
            handlers.append(
                v.__module__ + '.' + v.__name__
            )

        ui_modules = []
        for v in plugin._ui_modules:
            _application.ui_modules[v.__name__] = v
            ui_modules.append(
                v.__module__ + '.' + v.__name__
            )

        pl = models.Plugins()
        pl.name        = name
        pl.bind        = Json.encode(register._targets)
        pl.handlers    = Json.encode(handlers)
        pl.ui_modules  = Json.encode(ui_modules)

        if plugin.get_form() :
            pl.config = Json.encode(plugin.get_form().get_default_values())
        pl.save()

        # 安装路由
        if len(plugin._handlers) > 0 :
            from xcat.web import Application
            cache.client.set(Application._sync_key,Date.time())

        reset()
        
class Register(object):
    '''
    插件注册表
    '''
    
    def __init__(self):
        self._handler = False
        self._targets = {}
        self._events  = (
            'on_init' , 
            'before_execute' , 
            'before_render' ,
            'on_finish' ,
        )

    # 注册对象
    def handler(self):
        def decorator(handler):
            self._handler = handler
            return handler
        return decorator

    # 绑定事件
    def bind(self, event, targets):
        def decorator(func):
            if event in self._events:
                self._targets.setdefault(event,[])
                for v in targets :
                    self._targets[event].append({
                        'target' : v ,
                        'callback' : func.__name__
                    })
            return func
        return decorator



class Base(object):
    """
      插件的基类
    """

    def __init__(self):

        self.model = self.__class__.__module__

  
        # 运行时的上下文
        self._context = {}

        # 插件的控制器
        self._handlers = []

        # ui modules
        self._ui_modules = []


    '''
      安装时执行

    '''
    def install(self):
        pass

    '''
      卸载时执行
    '''
    def uninstall(self):
        pass

    def get_form(self):
        return False

    # 取配置
    @property
    def config(self):
        return get_config( self.__class__.__module__ \
                           + '.' + self.__class__.__name__ , {} )

    def set_config(self, config):
        full_name = self.__class__.__module__ + '.' + self.__class__.__name__
        set_config(full_name, config)

    '''
      添加控制器
    '''
    def add_handler(self, handler):
        handler = self.__class__.__module__ + '.handlers.' + handler
        handler = import_object(handler)
        if handler not in self._handlers:
            self._handlers.append(handler)

    '''
      添加 UI models
    '''
    def add_ui_module(self, ui_module):
        ui_module = self.__class__.__module__ + '.uimodules.' + ui_module
        ui_module = import_object(ui_module)
        if ui_module not in self._ui_modules:
            self._ui_modules.append(ui_module)

