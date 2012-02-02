#coding=utf-8
__author__ = 'vfasky'

import core.web.form as Qform
import core.db as Qdb
import app.model.sys

PLUGIN_TYPE = ( 'beforeExecute' , 'beforeRender' )

'''
插件基类
'''
class base:

    def __init__(self):
        self._db = Qdb.base()
        # 连接的目录
        self._target = []
        self._config = app.model.sys.plugin().getConfig( self.__class__.__name__ )

    # 取配置
    def getConfig(self):
        # 可以重写,定义默认值
        return self._config

    # 添加接口位置
    def addInterface(self , type , **cfg):
        if type in PLUGIN_TYPE \
        and cfg.has_key('target') \
        and cfg.has_key('action'):
            self._target.append({
                'type' : type ,
                'target' : cfg['target'] ,
                'action' : cfg['action']
            })
            return True
        return False

    # 配置表单,返回False为没有
    def config(self):
        return False

    # 激活插件时执行
    def activate(self):
        return False

