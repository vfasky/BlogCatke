#coding=utf-8

'''
  SAE 的 入口文件
  --------------

  @author vfasky@gmail.com
'''

import sys
import os

# 设置系统编码为utf8
code = sys.getdefaultencoding()
if code != 'utf8':
    reload(sys)
    sys.setdefaultencoding('utf8')


# 加入virtualenv.bundle目录
# @link http://appstack.sinaapp.com/static/doc/release/testing/tools.html#virtualenv
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'virtualenv.bundle'))

# 加入第三方类库搜索路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

try:
    
    # 加载程序配置
    from catke import config
    from xcat import cache
    # 引入Database
    from xcat import Database

    # 取缓存实例
    cache.client = getattr(cache, config.settings['xcat_cache'][config.settings['run_mode']])()


    # 加载数据库配置
    Database.load_config(
        config.settings['database'].get(config.settings['run_mode'],False)
    )

    import xcat.web
    import xcat.plugins
    from catke import uimodules

    # 加载UImodel
    config.settings['ui_modules'] = uimodules

    # run taoke
    from catke.handlers import *
    application = xcat.web.Application([],**config.settings)

    # 为插件注册 application
    xcat.plugins.register_app(application)
    # 绑定ACL
    xcat.web.Route.acl(application)

    # 绑定路由
    xcat.web.Route.routes(application)


except Exception, e:
    print str(e)



# 本地环境，启动 server
if 'SERVER_SOFTWARE' not in os.environ:
    import tornado.ioloop
    application.listen(config.settings['port'][config.settings['run_mode']])
    tornado.ioloop.IOLoop.instance().start()