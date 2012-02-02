#coding=utf-8
__author__ = 'vfasky'

import app.plugin
import markdown2
class editMarkdown(app.plugin.base):
    '''
    Markdow 编辑器
    '''

    # 激活插件是执行
    def activate(self):
        self.addInterface('beforeRender' , target = 'app.controller.admin.fatArticle' , action = 'initEdit')
        self.addInterface('beforeRender' , target = 'app.controller.admin.fatPage' , action = 'initEdit')

        self.addInterface('beforeRender' , target = 'app.controller.default.index' , action = 'renderList')
        self.addInterface('beforeRender' , target = 'app.controller.default.feed' , action = 'renderList')
        self.addInterface('beforeRender' , target = 'app.controller.default.category' , action = 'renderList')
        self.addInterface('beforeRender' , target = 'app.controller.default.tag' , action = 'renderList')

        self.addInterface('beforeRender' , target = 'app.controller.default.post' , action = 'render')
        self.addInterface('beforeRender' , target = 'app.controller.default.page' , action = 'render')

    # 解释单一内容
    def render(self, this, template_name, **kwargs):
        if 'post' in kwargs:
            kwargs['post'].text = markdown2.markdown( kwargs['post'].text )

        elif 'page' in kwargs:
            kwargs['page'].text = markdown2.markdown( kwargs['page'].text )
        return {
            'this' : this ,
            'template_name' : template_name ,
            'kwargs' : kwargs
        }

    # 解释列表内容
    def renderList(self, this, template_name, **kwargs):

        if 'list' in kwargs:
            list2 = []
            for v in kwargs['list']:
                v.text = markdown2.markdown( v.text )
                list2.append( v )

            list = list2

        return {
            'this' : this ,
            'template_name' : template_name ,
            'kwargs' : kwargs
        }

    # 初始化编辑器
    def initEdit(self, this, template_name, **kwargs):
        if 'plugin_footer' not in kwargs:
            kwargs['plugin_footer'] = []

        kwargs['plugin_footer'].append('<link rel="stylesheet" type="text/css" href="'+ this.static_url('plugins/editMarkdown/markitup/skins/simple/style.css') +'" />')
        kwargs['plugin_footer'].append('<link rel="stylesheet" type="text/css" href="'+ this.static_url('plugins/editMarkdown/markitup/sets/markdown/style.css') +'" />')
        kwargs['plugin_footer'].append('<script type="text/javascript" src="'+ this.static_url('plugins/editMarkdown/qcore.js') +'"></script>')
        kwargs['plugin_footer'].append('<script type="text/javascript" src="'+ this.static_url('plugins/editMarkdown/markitup/jquery.markitup.js') +'"></script>')
        kwargs['plugin_footer'].append('<script type="text/javascript" src="'+ this.static_url('plugins/editMarkdown/markdown.js') +'"></script>')
        kwargs['plugin_footer'].append('<script type="text/javascript" src="'+ this.static_url('plugins/editMarkdown/main.js') +'"></script>')


        return {
            'this' : this ,
            'template_name' : template_name ,
            'kwargs' : kwargs
        }