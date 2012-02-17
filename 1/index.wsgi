#coding=utf-8
import tornado.wsgi
import sae
import os
import sys
# 设置系统编码为utf8
code = sys.getdefaultencoding()
if code != 'utf8':
	reload(sys)
	sys.setdefaultencoding('utf8')

# 控制器
import app.controller.default
import app.controller.admin

# ui_modules
import uimodules

# 设置
settings = {
    'debug': True,
    'gzip': True,
    'Version' : '1.0.3.2',
    'cookie_secret' : '"61o42QsKXQAGaYdvfasky5aDfpsu$^EQnp2XdTP1o/Vo=', #请修改随机值
    'root_path' : os.path.dirname(__file__),
    'template_path' : os.path.join(os.path.dirname(__file__), "app/view/"),
    'static_path' : os.path.join(os.path.dirname(__file__), "static"),
    'acl' : {
        'db_name' : 'sys_acl' , # 存放 acl 的表名
        'default' : { # 默认的 acl 规则
            'allow' : ['ACL_EVERYONE'] # 容许所有人
        }
    },
    'session' :{
        'store' :  'Memcache', # session 的存放方式
        'args' : {  } # 附加参数
    },
    'ui_modules' : uimodules,
    'autoescape' : None ,
}

app = tornado.wsgi.WSGIApplication([
    (r"/", app.controller.default.index),
    (r"/post/(.+)$", app.controller.default.post),
    (r"/page/(.+)$", app.controller.default.page),
    (r"/tag/(.+)/$", app.controller.default.tag),
    (r"/category/(.+)/$", app.controller.default.category),
    (r"/feed/", app.controller.default.feed),
    (r"/login", app.controller.admin.login),
    (r"/logout", app.controller.admin.logout),
    (r"/install", app.controller.admin.install),
    (r"/admin/user", app.controller.admin.user),
    (r"/admin/role", app.controller.admin.role),
    (r"/admin/acl", app.controller.admin.acl),
    (r"/admin/fatArticle", app.controller.admin.fatArticle),
    (r"/admin/articles", app.controller.admin.articles),
    (r"/admin/pages", app.controller.admin.pages),
    (r"/admin/delArticle", app.controller.admin.delArticle),
    (r"/admin/profile", app.controller.admin.profile),
    (r"/admin/fatPage", app.controller.admin.fatPage),
    (r"/admin/option", app.controller.admin.option),
    (r"/admin/template", app.controller.admin.template),
    (r"/admin/category", app.controller.admin.category),
    (r"/admin/tags", app.controller.admin.tags),
    (r"/admin/upload", app.controller.admin.upload),
    (r"/admin/comment", app.controller.admin.comment),
    (r"/admin/plugin", app.controller.admin.plugin),
    (r"/(.+)$", app.controller.default._404),
], **settings)

application = sae.create_wsgi_app(app)