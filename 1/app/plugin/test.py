#coding=utf-8
__author__ = 'vfasky'

import app.plugin


class test(app.plugin.base):
    '''
    测试插件
    @author vfasky
    '''

    # 激活插件是执行
    def activate(self):
        self.addInterface('beforeExecute' , {
            'target' : 'app.controller.default' ,
            'action' : 'test'
        })

    # 测试
    def test(self,  this , *args, **kwargs):
        print 'hello word'
        return this