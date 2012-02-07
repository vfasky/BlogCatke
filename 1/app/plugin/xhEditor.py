#coding=utf-8
__author__ = 'vfasky'

import app.plugin
import markdown2
class xhEditor(app.plugin.base):
    '''
    xhEditor(http://xheditor.com) 可视化编辑器
    '''

    # 激活插件时执行
    def activate(self):
        self.addInterface('beforeRender' , target = 'app.controller.admin.fatArticle' , action = 'initEdit')
        self.addInterface('beforeRender' , target = 'app.controller.admin.fatPage' , action = 'initEdit')



    # 初始化编辑器
    def initEdit(self, this, template_name, **kwargs):
        if 'plugin_footer' not in kwargs:
            kwargs['plugin_footer'] = []


        kwargs['plugin_footer'].append('<script type="text/javascript" src="'+ this.static_url('plugins/xhEditor/xheditor-1.1.12-zh-cn.min.js') +'"></script>')
        kwargs['plugin_footer'].append('<script type="text/javascript" src="'+ this.static_url('plugins/xhEditor/main.js') +'"></script>')


        return {
            'this' : this ,
            'template_name' : template_name ,
            'kwargs' : kwargs
        }