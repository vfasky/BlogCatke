#coding=utf-8
__author__ = 'vfasky'

'''
实现插件机制
'''
import app.model.sys
import functools

pluginModle = app.model.sys.plugin()

# 执行控制器动作之前调用
def beforeExecute(method):
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        thisAction = self.__class__.__module__ + '.' + self.__class__.__name__
        pluginList = pluginModle.list()

        if thisAction in pluginList['beforeExecute'] :
            this = self
            for plug in pluginList['beforeExecute'][ thisAction ] :
                pluginObj = pluginModle.getInstantiate( plug['name'] )
                ret = getattr( pluginObj , plug['action'] )( this, *args, **kwargs )

                this = ret['this']
                args = ret['args']
                kwargs = ret['kwargs']
            return method(this, *args, **kwargs)
        else :
            return method(self, *args, **kwargs)

    return wrapper

# 渲染之前调用
def beforeRender(method):
    @functools.wraps(method)
    def wrapper(self, template_name, **kwargs):
        thisAction = self.__class__.__module__ + '.' + self.__class__.__name__
        pluginList = pluginModle.list()

        if thisAction in pluginList['beforeRender'] :
            this = self
            for plug in pluginList['beforeRender'][ thisAction ] :

                pluginObj = pluginModle.getInstantiate( plug['name'] )
                ret = getattr( pluginObj , plug['action'] )( this, template_name, **kwargs )

                this = ret['this']
                template_name = ret['template_name']
                kwargs = ret['kwargs']

            return method(this, template_name, **kwargs)
        else :
            return method(self, template_name, **kwargs)

    return wrapper
