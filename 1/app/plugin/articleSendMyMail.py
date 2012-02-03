#coding=utf-8
__author__ = 'vfasky'

import app.plugin

try:
    from sae.mail import EmailMessage
    isDev = False
except:
    isDev = True

class articleSendMyMail(app.plugin.base):
    '''
    将文章发到我的邮箱
    '''

    # 激活插件时执行
    def activate(self):
        self.addInterface('afterExecute' , target = 'app.controller.admin.fatArticle' , action = 'send')
        self.addInterface('afterExecute' , target = 'app.controller.admin.fatPage' , action = 'send')

    # 取配置
    def getConfig(self):
        return self._config and self._config or False

    # 配置表单
    def config(self):
        form = self._form.Form()
        form.add( self._form.Input('email' , 'isEmail' , label='邮箱') )
        form.add( self._form.Input('password' , 'notEmpty' , label='密码' ) )
        form.add( self._form.Input('host' , 'notEmpty' , label='SMTP主机' ) )
        form.add( self._form.Input('port' , 'isNumber' , value=25, label='SMTP端口' ) )
        form.add( self._form.Select('isTLS' , data = [
                { 'value' : 'False' , 'label' : '否' } ,
                { 'value' : 'True' , 'label' : '是' }
        ] , value='False' , label='是否启用TLS' ) )
        return form

    def send(self, this ,chunk=None):
        config = self.getConfig()
        if config and 'POST' == this.request.method:
            title = this.get_argument('title')
            text = this.get_argument('text')
            if False == 'isDev':
                isTLS = config['isTLS'] == 'True' and True or False

                m = EmailMessage()
                m.to = config['email']
                m.subject = title
                m.html = text
                m.smtp = ( config['host'] , int(config['port']), config['email'], config['password'], isTLS)
                m.send()
            else:
                print title
                print text


        return {
            'this' : this ,
            'chunk' : chunk
        }