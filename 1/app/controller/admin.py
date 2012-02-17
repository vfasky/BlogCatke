#coding=utf-8
__author__ = 'vfasky'


import core.web
import core.web.form
import tornado.escape
import time
import os
import app.model.sys
import app.model.uc
import app.model.bc
import app.controller
try:
    import sae.storage
    isDev = False
except:
    isDev = True

class BlogHandler(core.web.RequestHandler):

    @app.controller.beforeRender
    def render(self, template_name, **kwargs):
        if 'plugin_header' not in kwargs:
            kwargs['plugin_header'] = []
        if 'plugin_footer' not in kwargs:
            kwargs['plugin_footer'] = []
        return self.write(self.render_string( template_name, **kwargs))

    @app.controller.afterExecute
    def finish(self, chunk=None):
        """Finishes this response, ending the HTTP request."""
        if self._finished:
            return False

        if chunk is not None: self.write(chunk)

        # Automatically support ETags and add the Content-Length header if
        # we have not flushed any content yet.
        if not self._headers_written:
            if (self._status_code == 200 and
                self.request.method in ("GET", "HEAD") and
                "Etag" not in self._headers):
                etag = self.compute_etag()
                if etag is not None:
                    inm = self.request.headers.get("If-None-Match")
                    if inm and inm.find(etag) != -1:
                        self._write_buffer = []
                        self.set_status(304)
                    else:
                        self.set_header("Etag", etag)
            if "Content-Length" not in self._headers:
                content_length = sum(len(part) for part in self._write_buffer)
                self.set_header("Content-Length", content_length)

        if hasattr(self.request, "connection"):
            # Now that the request is finished, clear the callback we
            # set on the IOStream (which would otherwise prevent the
            # garbage collection of the RequestHandler when there
            # are keepalive connections)
            self.request.connection.stream.set_close_callback(None)

        if not self.application._wsgi:
            self.flush(include_footers=True)
            self.request.finish()
            self._log()
        self._finished = True

'''
安装
'''
class install(core.web.RequestHandler):
    # 是否容许安装
    def allowInstallation(self):
        if False == self.mysqlIsConnection() :
            return True
        try:
            if 0 == app.model.uc.user().find().count() :
                return True
        except:
            return True
        return False

    # 检查mysql是否可连接
    def mysqlIsConnection(self):
        try:
            import core.db
            core.db.base().query('show tables;')
            return True
        except:
            return False

    # 检查storage是否可连接
    def storageIsConnection(self):
        if isDev :
            return True

        try:
            s = sae.storage.Client()
            for ns in s.list_domain() :
                if 'storage' == ns :
                    return True

            return False
        except:
            return False

    # 检查memcache是否可连接
    def memcacheIsConnection(self):
        import pylibmc
        try:
            mc = pylibmc.Client()
            mc.set("memcache-test", "True")
            return mc.get("memcache-test") == "True" and True or False
        except:
            return False

    def form(self):
        form = core.web.form.Form()
        form.add( core.web.form.Input('email', 'notEmpty' , 'isEmail' , label='邮箱') )
        form.add( core.web.form.Input('password', 'notEmpty' ,  label='密码') )
        form.add( core.web.form.Input('nickname' , 'notEmpty' , label='昵称') )
        return form

    def get(self):
        step = int( self.get_argument('step' , '1') )

        if False == self.allowInstallation() and step != 3:
            return self.error( msg = '已经完成安装' )


        # 安装第一步
        if step == 1:
            return self.render("admin/install.html" ,
                               mysqlIsConnection = self.mysqlIsConnection() ,
                               storageIsConnection = self.storageIsConnection() ,
                               memcacheIsConnection = self.memcacheIsConnection() ,
                               step = step
                              )
        # 安装第二步
        elif step == 2:
            return self.render("admin/install-02.html" , form = self.form() )

        else:
            return self.render("admin/install-03.html")

    def post(self):
        if False == self.allowInstallation():
            return self.error( msg = '已经完成安装' )

        if self.mysqlIsConnection() and self.storageIsConnection() and self.memcacheIsConnection() :

            step = int( self.get_argument('step' , '1') )

            # 安装第一步
            if step == 1:
                file = open( os.path.join( self.settings['root_path'] , 'qcore.sql' ) , 'r' )
                sql = file.read().split(';')
                del sql[ len(sql) - 1 ]
                import core.db
                dbModel = core.db.base()
                for v in sql:
                    dbModel.db.execute( v )

                return self.redirect('/install?step=2')

            elif step == 2:
                form = self.form()
                # 资料编辑
                if form.validators( self.request.arguments ):
                    userModel = app.model.uc.user()
                    import hashlib

                    userModel.attr = form.values
                    userModel.attr['encryption'] = app.model.uc.user.buildEncryption()
                    m = hashlib.md5()
                    m.update( userModel.attr['password'] )
                    m.update( userModel.attr['encryption'] )
                    userModel.attr['password'] = m.hexdigest()
                    id = userModel.add()

                    # 绑定管理员
                    userModel.bindRoles( id , [1] )

                    return self.redirect('/install?step=3')

                else:
                    return self.error( msg = form.msg )

        else:
            return self.error( msg = '请检查安装环境' )

'''
基本设置
'''
class option(BlogHandler):
    # 配置
    _options = app.model.sys.options()

    def form(self):
        form = core.web.form.Form()
        form.add( core.web.form.Input('title', 'notEmpty' , label='站点名称')  )
        form.add( core.web.form.Input('subtitle', 'notEmpty' , label='副标题')  )
        form.add( core.web.form.Input('keywords' , 'notEmpty' , label='关键词') )
        form.add( core.web.form.Textarea('desc' , 'notEmpty' , label='站点描述') )
        return form

    @app.controller.beforeExecute
    @core.web.acl
    def get(self):
        if not option._options['site']:
            option._options['site'] = {
                'title' : '' ,
                'subtitle' : '' ,
                'desc' : '' ,
                'keywords' : ''
            }

        self.render("admin/option.html" ,  data = option._options['site'] , form = self.form() )

    @app.controller.beforeExecute
    @core.web.acl
    def post(self):
        form = self.form()

        if form.validators( self.request.arguments ):
            option._options['site'] = form.values


        self.redirect('/admin/option')

'''
插件管理
'''
class plugin(BlogHandler):
    # 取插件列表
    def getPlugins(self):
        path = os.path.join( self.settings['root_path'] , 'app' , 'plugin' )
        init = str( os.path.join( path , '__init__.py') )
        key  = init.split( '__init__.py' )

        import glob
        list = glob.glob( os.path.join( path , '*.py') )

        plugins = []
        for name in list:
            name = str(name)
            if init != name:
                plugins.append( name.replace( key[0] , '' ).replace('.py' , '') )

        return plugins

    # 取插件信息
    def getInfo(self,name):
        plugin = app.model.sys.plugin.getInstantiate(name)

        return {
            'desc' : tornado.escape.linkify( plugin.__class__.__doc__ ) ,
            'isConfig' : plugin.config() and True or False ,
            'name' : name ,
        }

    # 启用插件
    def enable(self,name):
        pluginModel = app.model.sys.plugin()
        plugin = pluginModel.getInstantiate( name )
        # 初始化插件
        plugin.activate()
        cfg = {
            'interface' : plugin._target ,
            'config' : plugin.getConfig() ,
            'desc' : plugin.__class__.__doc__
        }
        pluginModel.add(name , **cfg)
        self.write( tornado.escape.json_encode({'success' : True}) )
        return True

    # 禁用插件
    def disable(self,name):
        pluginModel = app.model.sys.plugin()
        if name in pluginModel.getList():
            plugin = pluginModel.getInstantiate( name )
            # 禁用插件
            plugin.disable()
            pluginModel.remove(name)
        self.write( tornado.escape.json_encode({'success' : True}) )
        return True

    # 取插件表单
    def getForm(self,name):
        enables = app.model.sys.plugin().getList()
        if name in enables:
            pluginModel = app.model.sys.plugin()
            plugin = pluginModel.getInstantiate(name)
            form = plugin.config()
            return form
        return False

    @app.controller.beforeExecute
    @core.web.acl
    def get(self):
        enables = app.model.sys.plugin().getList()
        # 插件配置
        if self.get_argument('type' , False) == 'config' and self.get_argument('name' , False) :
            name = self.get_argument('name')
            form = self.getForm( name )
            if form:
                return self.render("admin/plugin-config.html" , data = app.model.sys.plugin().getConfig(name) ,  form = form , info = self.getInfo(name) )

        plugins = self.getPlugins()

        list = []
        for name in plugins:
            if name not in enables:
                list.append( self.getInfo(name) )

        enableList = []
        for name in enables:
            enableList.append( self.getInfo(name) )

        self.render("admin/plugin.html" ,  enableList = enableList , list = list )

    @app.controller.beforeExecute
    @core.web.acl
    def post(self):
        type = self.get_argument('type' , False)
        if type:
            if 'enable' == type and self.get_argument('name' , False):
                return self.enable( self.get_argument('name') )
            elif 'disable' == type and self.get_argument('name' , False):
                return self.disable( self.get_argument('name') )
            elif 'config' == type and self.get_argument('name' , False):
                name = self.get_argument('name')
                form = self.getForm( name )
                if form and form.validators( self.request.arguments ):
                    pluginModel = app.model.sys.plugin()
                    data = pluginModel.getData( name )
                    data['config'] = form.values
                    pluginModel.setData(name , **data)
                    self.redirect('/admin/plugin')

'''
上传
'''
class upload(BlogHandler):
    @app.controller.beforeExecute
    @core.web.acl
    def post(self):

        if not self.request.files.has_key('filedata'):
            return self.write( tornado.escape.json_encode({ 'success': False , 'msg' : '没有文件被上传' }) )

        import hashlib

        fileName = str( self.get_argument('filename') )
        list = fileName.split('.')
        suffix = list[ len(list) - 1 ]

        m = hashlib.md5()
        m.update(fileName)
        m.update( str(time.time()) )
        fileName = str( m.hexdigest() ) + '.' + suffix

        # 初始化一个Storage客户端。
        s = sae.storage.Client()
        ob = sae.storage.Object(self.request.files['filedata'][0]['body'])

        s.put('storage', fileName , ob)
        return self.write( tornado.escape.json_encode({ 'success': True , 'url' : s.url('storage' , fileName ) , 'type' : self.get_argument('type') }) )

'''
评论管理
'''
class comment(BlogHandler):

    def form(self):
        form = core.web.form.Form()
        form.add( core.web.form.Input('disqus_shortname', 'notEmpty' , label='Disqus Site Shortname:') )
        return form

    @app.controller.beforeExecute
    @core.web.acl
    def get(self):
        if not option._options['site_comment']:
            option._options['site_comment'] = {
                'disqus_shortname' : ''
            }

        self.render("admin/comment.html" ,  data = option._options['site_comment'] , form = self.form() )

    @app.controller.beforeExecute
    @core.web.acl
    def post(self):
        form = self.form()

        if form.validators( self.request.arguments ):
            option._options['site_comment'] = form.values


        self.redirect('/admin/comment')

'''
tag 管理
'''
class tags(BlogHandler):

    def form(self):
        form = core.web.form.Form()
        form.add( core.web.form.Hidden('id') )
        form.add( core.web.form.Input('name' , 'notEmpty' , label='名称') )
        return form

    @app.controller.beforeExecute
    @core.web.acl
    def get(self):
        tags = app.model.bc.meta().find('[type] = %s' , 'tag')\
                                  .order('[order] DESC ,[id] DESC')\
                                  .fields('[id],[name],[order]')\
                                  .getAll()

        self.render("admin/tags.html" ,  tags = tags , form = self.form() )

    @app.controller.beforeExecute
    @core.web.acl
    def post(self):
        form = self.form()
        metaModel = app.model.bc.meta()

        # 删除
        if self.get_argument('deleteId' , False):
            metaModel.tagDelete( self.get_argument('deleteId') )
            return self.write( tornado.escape.json_encode( { 'success' : True } ) )

        if form.validators(self.request.arguments) :
            # 编辑
            if self.get_argument('id' , False):
                metaModel.attr = { 'name' : form.values['name'] }
                metaModel.save('[id] = %s' , form.values['id'])
                return self.write( tornado.escape.json_encode( { 'success' : True } ) )
            # 添加
            else:
                metaModel.attr = { 'name' : form.values['name'] }
                metaModel.attr['type'] = 'tag'
                metaModel.add()
                return self.redirect('/admin/tags')


        return self.write( tornado.escape.json_encode( { 'success' : False , 'msg' : form.msg } ) )

'''
文章分类
'''
class category(BlogHandler):

    def form(self):
        form = core.web.form.Form()
        form.add( core.web.form.Hidden('id') )
        form.add( core.web.form.Input('name' , 'notEmpty' , label='名称') )
        return form

    @app.controller.beforeExecute
    @core.web.acl
    def get(self):
        categorys = app.model.bc.meta().find('[type] = %s' , 'category')\
                                       .order('[order] DESC ,[id] DESC')\
                                       .fields('[id],[name],[order]')\
                                       .getAll()

        self.render("admin/category.html" ,  categorys = categorys , form = self.form() )

    @app.controller.beforeExecute
    @core.web.acl
    def post(self):
        form = self.form()
        metaModel = app.model.bc.meta()

        # 删除
        if self.get_argument('deleteId' , False):
            metaModel.categoryDelete( self.get_argument('deleteId') )
            return self.write( tornado.escape.json_encode( { 'success' : True } ) )

        if form.validators(self.request.arguments) :
            form.values['name'] = tornado.escape.xhtml_escape(form.values['name'])
            # 编辑
            if self.get_argument('id' , False):
                metaModel.attr = { 'name' : form.values['name'] }
                metaModel.save('[id] = %s' , form.values['id'])
                return self.write( tornado.escape.json_encode( { 'success' : True } ) )
            # 添加
            else:
                metaModel.attr = { 'name' : form.values['name'] }
                metaModel.attr['type'] = 'category'
                metaModel.add()
                return self.redirect('/admin/category')


        return self.write( tornado.escape.json_encode( { 'success' : False , 'msg' : form.msg } ) )

'''
风格设置
'''
class template(BlogHandler):

    def getTemplates(self):
        path = os.path.join( self.settings['template_path'] , 'template' )
        templates = []
        for name in os.listdir( path ):
            if name != '.svn' :
                templates.append( name )
        return  templates

    @app.controller.beforeExecute
    @core.web.acl
    def get(self):
        templates = self.getTemplates()

        if not option._options['site_templates'] and len( templates ) > 0 :
            option._options['site_templates'] = templates[0]

        self.render('admin/template.html' , siteTemplate = option._options['site_templates'] , templates = templates )

    @app.controller.beforeExecute
    @core.web.acl
    def post(self):
        name = self.get_argument('name' , False)
        if name :
            isPath = False
            for path in self.getTemplates():
                if path == name:
                    option._options['site_templates'] = path
                    isPath = True
                    return self.write( tornado.escape.json_encode( { 'success' : True } ) )

            if False == isPath:
                return self.write( tornado.escape.json_encode( { 'success' : False , 'msg' : '文件夹不存在' } ) )
        else:
            return self.write( tornado.escape.json_encode( { 'success' : False , 'msg' : '数据为空' } ) )

'''
文章列表
'''
class articles(BlogHandler):

    @app.controller.beforeExecute
    @core.web.acl
    def get(self):
        contentModel = app.model.bc.content()
        page = self.get_argument('page',1)
        db = contentModel.find().limitPage( page  , 20)\
                                .where('[type] = %s' , 'post')\
                                .order('[id] DESC , [order] DESC')\
                                .fields('[id] , [title] , [created]')

        pagination = db.getPagination()
        contents = db.query()
        list = []

        for v in contents:

            v['categoryStr'] = app.model.bc.content.category( v['id'] )['name']
            v['createdStr'] = time.strftime('%Y-%m-%d %H:%M' , time.localtime(v['created']) )
            list.append( v )

        self.render("admin/articles.html" ,  list = list , pagination = pagination )

'''
页面列表
'''
class pages(BlogHandler):
    @app.controller.beforeExecute
    @core.web.acl
    def get(self):
        contentModel = app.model.bc.content()
        page = self.get_argument('page',1)
        db = contentModel.find().limitPage( page  , 20)\
                                .where('[type] = %s' , 'page')\
                                .order('[id] DESC , [order] DESC')\
                                .fields('[id] , [title] , [created]')

        pagination = db.getPagination()
        contents = db.query()
        list = []

        for v in contents:
            v['createdStr'] = time.strftime('%Y-%m-%d %H:%M' , time.localtime(v['created']) )
            list.append( v )

        self.render("admin/pages.html" ,  list = list , pagination = pagination )

'''
删除文章
'''
class delArticle(BlogHandler):
    @app.controller.beforeExecute
    @core.web.acl
    def post(self):
        id = self.get_argument('id' , False)
        if id:
            app.model.bc.content.remove( id )
        return self.write( tornado.escape.json_encode( {'success':True} ) )

'''
写页面
'''
class fatPage(BlogHandler):

    def form(self):
        form = core.web.form.Form()
        form.add( core.web.form.Hidden('id') )

        form.add( core.web.form.Input('title' , 'notEmpty' , label='标题') )
        form.add( core.web.form.Input('slug' , 'notEmpty' , label='缩略名') )
        form.add( core.web.form.Input('tags' ,  label='tag') )
        form.add( core.web.form.Textarea('text' , 'notEmpty' , label='' , rows="16") )

        return form

    @app.controller.beforeExecute
    @core.web.acl
    def get(self):
        data = {}
        thisTags = []
        if False != self.get_argument('id' , False):
            data = app.model.bc.content().find('[id] = %s' , int( self.get_argument('id') )).query()
            thisTags = app.model.bc.content.tags( self.get_argument('id') )

        tags = app.model.bc.meta().find('[type] = %s' , 'tag').fields('[name]').getAll()
        self.render("admin/fatArticle.html" , form = self.form() , data =  data , tags = tags , thisTags = thisTags )

    @app.controller.beforeExecute
    @core.web.acl
    def post(self):
        form = self.form()

        if form.validators( self.request.arguments ):
            # 添加
            if not form.values['id']:
                id = False

                # 确保缩略名唯一
                if 0 != app.model.bc.content().find('[slug] = %s' , form.values['slug']).count():
                    return self.error( msg = '缩略名已经存在' )

            # 编辑
            else:
                id = form.values['id'][0]
                id = int(id)

                # 确保缩略名唯一
                if 0 != app.model.bc.content().find('[slug] = %s AND [id] != %s' , form.values['slug'] , id).count():
                    return self.error( msg = '缩略名已经存在' )

                # 删除tag关联
                app.model.bc.content.tagDelete( id )

            # 标记为页面
            form.values['type'] = 'page'
            # tags
            tags = form.values.pop('tags' , '[]')

            data = form.values

            data['user_id'] = self.acl_current_user()['id']

            contentModel = app.model.bc.content()
            contentModel.attr = data

            # 编辑
            if False != id :
                del contentModel.attr['id']
                contentModel.attr['modified'] = time.time()
                contentModel.save('[id] = %s' , id)
            else : # 添加
                contentModel.attr['created'] = time.time()
                id = contentModel.add()

            # 关联tag
            app.model.bc.content.tagAdd( tags , id )
        else:
            return self.error( msg = form.msg )

        self.redirect("/admin/pages")

'''
写文章
'''
class fatArticle(BlogHandler):

    def form(self):
        form = core.web.form.Form()
        form.add( core.web.form.Hidden('id') )

        form.add( core.web.form.Input('title' , 'notEmpty' , label='标题') )
        form.add( core.web.form.Input('slug' , 'notEmpty' , label='缩略名') )


        #分类
        category = app.model.bc.meta().find('[type] = %s' , 'category').order('[order] DESC').getAll()
        categoryData = []
        for v in category:
            categoryData.append( { 'label' : v['name'] , 'value' : v['id'] } )

        form.add( core.web.form.Select('category_id' , label='分类' , data=categoryData) )
        form.add( core.web.form.Input('tags' ,  label='tag') )
        form.add( core.web.form.Textarea('text' , 'notEmpty' , label='' , rows="16") )

        return form

    @app.controller.beforeExecute
    @core.web.acl
    def get(self):
        #return self.error(msg='s')
        data = {}
        thisTags = []
        if False != self.get_argument('id' , False):
            data = app.model.bc.content().find('[id] = %s' , int( self.get_argument('id') )).query()
            data['category_id'] = app.model.bc.content.category( data['id'] )['id']
            thisTags = app.model.bc.content.tags( self.get_argument('id') )

        tags = app.model.bc.meta().find('[type] = %s' , 'tag').fields('[name]').getAll()
        self.render("admin/fatArticle.html" , form = self.form() , data =  data , tags = tags , thisTags = thisTags )

    @app.controller.beforeExecute
    @core.web.acl
    def post(self):
        form = self.form()

        if form.validators( self.request.arguments ):

            # 添加
            if not form.values['id']:
                id = False

                # 确保缩略名唯一
                if 0 != app.model.bc.content().find('[slug] = %s' , form.values['slug']).count():
                    return self.error( msg = '缩略名已经存在' )

            # 编辑
            else:
                id = form.values['id'][0]
                id = int(id)

                # 确保缩略名唯一
                if 0 != app.model.bc.content().find('[slug] = %s AND [id] != %s' , form.values['slug'] , id).count():
                    return self.error( msg = '缩略名已经存在' )

                # 删除旧分类关联
                app.model.bc.content.categoryDelete( id )
                # 删除tag关联
                app.model.bc.content.tagDelete( id )


            metaId = form.values.pop('category_id')
            # tags
            tags = form.values.pop('tags' , '[]')

            data = form.values

            data['user_id'] = self.acl_current_user()['id']

            contentModel = app.model.bc.content()
            contentModel.attr = data

            # 编辑
            if False != id :
                del contentModel.attr['id']
                contentModel.attr['modified'] = time.time()
                contentModel.save('[id] = %s' , id)
            else : # 添加
                contentModel.attr['created'] = time.time()
                id = contentModel.add()

            # 关联分类
            metaHasContentModel = app.model.bc.metaHasContent()
            metaHasContentModel.attr = {
                'meta_id' : metaId ,
                'content_id' : id
            }

            # 关联tag
            app.model.bc.content.tagAdd( tags , id )

            metaHasContentModel.add()

            app.model.bc.meta().updateCount([{ 'meta_id' : metaId }])
        else:
            return self.error( msg = form.msg )

        self.redirect("/admin/articles")
'''
个人资料
'''
class profile(BlogHandler):

    def form(self):
        form = core.web.form.Form()
        form.add( core.web.form.Hidden('id' , 'notEmpty') )
        form.add( core.web.form.Input('email', 'notEmpty' , 'isEmail' , label='邮箱') )
        form.add( core.web.form.Input('nickname' , 'notEmpty' , label='昵称') )
        return form

    def passwordForm(self):
        form = core.web.form.Form()
        form.add( core.web.form.Password('password' , 'notEmpty' , label='用户密码') )
        form.add( core.web.form.Password('confirm' , 'notEmpty', label='确认密码') )
        return form

    @app.controller.beforeExecute
    @core.web.acl
    def get(self):
        import urllib, hashlib

        user = self.acl_current_user()
        data = app.model.uc.user().find('[id] = %s' , user['id'])\
                                  .fields('[id],[email],[nickname]')\
                                  .query()
        # 显示头像
        gravatarUrl = "http://cn.gravatar.com/avatar/" + hashlib.md5( data['email'] .lower()).hexdigest() + "?"
        gravatarUrl += urllib.urlencode({ 's': '100' })
        self.render("admin/profile.html" , userInfo = user , form = self.form() , data = data , passwordForm = self.passwordForm() , gravatarUrl = gravatarUrl )

    @app.controller.beforeExecute
    @core.web.acl
    def post(self):
        form = self.form()
        passwordForm = self.passwordForm()
        user = self.acl_current_user()
        userModel = app.model.uc.user()

        # 资料编辑
        if form.validators( self.request.arguments ):
            # 检查邮件是否重复
            if 0 != userModel.find('[email] = %s AND [id] != %s' , form.values['email'] , user['id']).count() :
                return self.error( msg = '邮箱已经存在!' )
            # 检查昵称是否重复
            if 0 != userModel.find('[nickname] = %s AND [id] != %s' , form.values['nickname'] , user['id']).count() :
                return self.error( msg = '昵称已经存在!' )

            userModel.attr = form.values
            userModel.save('[id] = %s' , user['id'])
        elif passwordForm.validators( self.request.arguments ):
            if passwordForm.values['password'] != passwordForm.values['confirm'] :
                return self.error( msg = '两次输入密码不相符' )
            
            import hashlib
            user = userModel.find('[id] = %s' , user['id']).query()
            m = hashlib.md5()
            m.update( passwordForm.values['password'] )
            m.update( user['encryption'] )

            userModel.attr = { 'password' : m.hexdigest() }
            userModel.save('[id] = %s' , user['id'])

        self.redirect("/admin/profile")


'''
会员管理
'''
class user(BlogHandler):

    def form(self):
        form = core.web.form.Form()
        form.add( core.web.form.Hidden('id' ) )
        form.add( core.web.form.Input('email', 'notEmpty' , 'isEmail' , label='邮箱') )
        form.add( core.web.form.Input('password' ,  label='密码') )
        form.add( core.web.form.Input('nickname' , 'notEmpty' , label='昵称') )
        return form

    def roleForm(self):
        roleModel = app.model.uc.role()
        roles = []
        for role in roleModel.find().getAll():
            roles.append( { 'value' : role['id'] , 'label' : role['name'] } )

        form = core.web.form.Form()
        form.add( core.web.form.Hidden('id' , 'notEmpty') )
        form.add( core.web.form.Checkbox('roleIds' , label = '角色' , data = roles ) )
        return form

    @app.controller.beforeExecute
    @core.web.acl
    def get(self):

        page = self.get_argument('page' , 1)
        db = app.model.uc.user().find().limitPage( page , 20 )
        pagination = db.getPagination()
        users = db.query()
        list = []

        for user in users:
            user['roleNames'] = app.model.uc.user.roleNamesToStr( user['id'] )
            user['roleIds'] = app.model.uc.user.roleIds( user['id'] )
            list.append( user )

        self.render("admin/user.html" , form = self.form() , list = list , roleForm = self.roleForm() , pagination = pagination )

    @app.controller.beforeExecute
    @core.web.acl
    def post(self):
        form = self.form()
        roleForm = self.roleForm()
        # 资料编辑
        if form.validators( self.request.arguments ):
            userModel = app.model.uc.user()
            import hashlib
            # 添加
            if not form.values['id']:
                userModel.attr = form.values
                userModel.attr['encryption'] = app.model.uc.user.buildEncryption()
                m = hashlib.md5()
                m.update( userModel.attr['password'] )
                m.update( userModel.attr['encryption'] )
                userModel.attr['password'] = m.hexdigest()
                userModel.add()
            # 编辑
            else:

                # 不为空,修改密码
                if form.values['password'] != None:
                    user = userModel.find('[id] = %s' , form.values['id']).query()
                    m = hashlib.md5()
                    m.update( form.values['password'] )
                    m.update( user['encryption'] )
                    form.values['password'] = m.hexdigest()
                else:
                    del form.values['password']
                userModel.attr = form.values
                userModel.save('[id] = %s' , form.values['id'])
        # 角色绑定
        elif roleForm.validators( self.request.arguments ):
            app.model.uc.user.bindRoles( roleForm.values['id'] , roleForm.values['roleIds'] )

        else:
            return self.error( msg = form.msg )

        self.redirect("/admin/user")
'''
权限控制
'''
class acl(BlogHandler):

    def form(self):
        rolesData = app.model.sys.acl.getRoles()

        form = core.web.form.Form()
        form.add( core.web.form.Hidden('id') )
        form.add( core.web.form.Input('uri' , 'notEmpty' , label = 'uri') )
        form.add( core.web.form.Input('desc' , 'notEmpty' , label = '描述') )
        form.add( core.web.form.Checkbox('deny' , data = rolesData , label = '禁止访问'  ) )
        form.add( core.web.form.Checkbox('allow' , data = rolesData , label = '允许访问'  ) )
        return form

    @app.controller.beforeExecute
    @core.web.acl
    def get(self):
        list = []
        acls = app.model.sys.acl().find().limitPage( 1 , 20 ).query()
        for acl in acls:
            data = acl
            data.denyStr = app.model.sys.acl.rolesDecode( acl.deny )
            data.allowStr = app.model.sys.acl.rolesDecode( acl.allow )
            if data.deny:
                data.deny = tornado.escape.json_decode( data.deny )
            if data.allow:
                data.allow = tornado.escape.json_decode( data.allow )

            list.append( data )

        self.render("admin/acl.html" , list = list , form = self.form()  )

    @app.controller.beforeExecute
    @core.web.acl
    def post(self):
        model = app.model.sys.acl()

        import pylibmc
        mc = pylibmc.Client()

        # 删除
        if self.get_argument('deleteId' , False) :
            data = model.find('[id] = %s' , int(self.get_argument('deleteId'))).query()
            # 清空缓存
            if data and mc.get('ACL_URI_' + str(data['uri'])):
                mc.delete('ACL_URI_' + str(data['uri']))

            model.delete('[id] = %s' , int(self.get_argument('deleteId')) )
            return self.write( tornado.escape.json_encode({ 'success' : True }) )

        form = self.form()
        if form.validators( self.request.arguments ):
            model.attr = form.values
            model.attr['deny'] = tornado.escape.json_encode( model.attr['deny'] )
            model.attr['allow'] = tornado.escape.json_encode( model.attr['allow'] )

            data = model.find('[id] = %s' , form.values['id']).query()

            # 清空缓存
            if data and mc.get('_ACL_URI_' + str(data['uri'])):
                mc.delete('_ACL_URI_' + str(data['uri']))

            # 添加
            if not form.values['id']:
                model.add()
            # 编辑
            else:
                model.save('[id] = %s' , form.values['id'] )
        self.redirect("/admin/acl")


'''
角色管理
'''

class role(BlogHandler):

    def form(self):
        form = core.web.form.Form()
        form.add( core.web.form.Hidden( 'id' ) )
        form.add( core.web.form.Input( 'code' , 'notEmpty' , label = '代码' ) )
        form.add( core.web.form.Input( 'name' , 'notEmpty' , label = '名称' ) )
        return form

    @app.controller.beforeExecute
    @core.web.acl
    def get(self):
        roles = app.model.uc.role().find().getAll()
        self.render("admin/role.html" , roles = roles ,form = self.form() )

    @app.controller.beforeExecute
    @core.web.acl
    def post(self):
        # 删除
        if self.get_argument('deleteId' , False) :
            app.model.uc.role().remove( self.get_argument('deleteId') )
            return self.write( tornado.escape.json_encode({ 'success' : True }) )

        form = self.form();
        if form.validators( self.request.arguments ):
            roleModel = app.model.uc.role()

            # 添加
            if None == form.values['id']:
                roleModel.attr = form.values
                roleModel.add()
            # 修改
            else:
                roleModel.attr = form.values
                roleModel.edit('id = %s' , form.values['id'])

        self.redirect("/admin/role")

'''
退出
'''
class logout(BlogHandler):
    @app.controller.beforeExecute
    def get(self):
        self.clear_acl_current_user()
        self.redirect("/login")

'''
登陆
'''
class login(BlogHandler):

    def form(self):
        form = core.web.form.Form()
        form.add(core.web.form.Input('userEmail', 'notEmpty', 'isEmail', label='邮箱'))
        form.add(core.web.form.Password('password', 'notEmpty', label='密码'))
        return form

    @app.controller.beforeExecute
    def get(self):
        self.render("login.html", form=self.form())

    @app.controller.beforeExecute
    def post(self):
        import time
        time.sleep(3)

        form = self.form()
        if form.validators(self.request.arguments):
            userModel = app.model.uc.user()
            data = userModel.find('[email] = %s', form.values['userEmail']).query()
            if not data:
                return self.error(msg='账户不存在 或 邮箱未能过验证')

            import hashlib


            m = hashlib.md5()
            m.update(form.values['password'])
            m.update(data['encryption'])
            if m.hexdigest() == data['password']:
                # 更新最后登陆时间
                userModel.attr = {'last_login_time': time.time()}
                userModel.save('[email] = %s', form.values['userEmail'])

                # 写入登陆信息
                roleCodes = app.model.uc.user.roleCodes(data['id'])
                self.set_acl_current_user(data, roleCodes)

                self.redirect("/admin/articles")
            else:
                return self.error(msg='密码错误')