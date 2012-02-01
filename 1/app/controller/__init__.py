#coding=utf-8
__author__ = 'vfasky'

'''
实现插件机制
'''

import functools
# 执行控制器动作之前调用
def beforeExecute(method):
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):

        #print self.request.method
        print str(self.__class__.__module__)
        return method(self, *args, **kwargs)

    return wrapper

# 渲染之前调用
def beforeRender(method):
    @functools.wraps(method)
    def wrapper(self, template_name, **kwargs):

        return method(self, template_name, **kwargs)

    return wrapper