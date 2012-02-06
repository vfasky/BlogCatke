#coding=utf-8
__author__ = 'vfasky'

import app.plugin

class statisticalCode(app.plugin.base):
    '''
    在底部插入统计代码
    '''

    # 激活插件时执行
    def activate(self):
        self.addInterface('beforeRender' , target = 'app.controller.default.index' , action = 'render')
        self.addInterface('beforeRender' , target = 'app.controller.default.category' , action = 'render')
        self.addInterface('beforeRender' , target = 'app.controller.default.tag' , action = 'render')
        self.addInterface('beforeRender' , target = 'app.controller.default.post' , action = 'render')
        self.addInterface('beforeRender' , target = 'app.controller.default.page' , action = 'render')

    # 取配置
    def getConfig(self):
        return self._config and self._config or False

    # 配置表单
    def config(self):
        form = self._form.Form()
        form.add( self._form.Textarea('code' , 'notEmpty' , label='统计代码') )
        return form

    # 在底部插入代码
    def render(self, this, template_name, **kwargs):
        if self.getConfig():
            if 'plugin_footer' not in kwargs:
                kwargs['plugin_footer'] = []
            kwargs['plugin_footer'].append( self.getConfig()['code'] )


        return {
            'this' : this ,
            'template_name' : template_name ,
            'kwargs' : kwargs
        }