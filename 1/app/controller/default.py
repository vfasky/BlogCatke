#coding=utf-8
import time

__author__ = 'vfasky'

import core.web
import core.web.form
import app.model.uc
import app.model.sys
import app.model.bc
import markdown2
import urllib
import tornado.escape
import pylibmc


'''
模板扩展
'''
class templatePlug:
    def __init__(self, handler, path, **kwargs):
        self._path = path
        self._kwargs = kwargs
        self._handler = handler

    # 包含模板
    def include(self, template_name):
        return self._handler.render_string(self._path + template_name, **self._kwargs)

    # 解释markdown
    def markdown(self , txt):
        return markdown2.markdown( txt )

    def date(self , format , timeStr):
        import time
        return time.strftime(format , time.localtime(timeStr) )

    # 页面列表
    def pageList(self):
        contentModel = app.model.bc.content()
        list = contentModel.find('[type] = %s AND [status] = %s' , 'page' , 'publish')\
                           .fields('[id],[title],[slug]')\
                           .order('[order] DESC , [id] DESC')\
                           .getAll()
        pages = []
        for v in list:
            v['url'] = '/page/' + urllib.quote( str(v['slug']) )
            pages.append( v )
        return pages

    # tag list
    def tagsList(self):
        metaModel = app.model.bc.meta()
        list = metaModel.find('[type] = %s' , 'tag').order('[count] DESC').fields('[id],[name],[count]').getAll()
        return list

    # 分类列表
    def categoryList(self):
        metaModel = app.model.bc.meta()
        list = metaModel.find('[type] = %s' , 'category').order('[order] DESC,[id] DESC').fields('[id],[name],[count]').getAll()
        return list

    # 取文章分类
    def getPostCategoryById(self,id):
        return app.model.bc.content.category( id )

    # 取内容的tags
    def getContentTagsById(self,id):
        return app.model.bc.content.tags( id )

    # 取昵称
    def getNicknameById(self,id):
        user = app.model.uc.user().find('[id] = %s' , int(id)).fields('[nickname]').query()
        if user:
            return user['nickname']
        return False


    # 最近文章
    def recentPosts(self , count = 10):
        contentModel = app.model.bc.content()
        list = contentModel.find('[type] = %s AND [status] = %s' , 'post' , 'publish')\
                           .fields('[id],[title],[slug]')\
                           .order('[order] DESC , [id] DESC')\
                           .limit(0 , int(count))\
                           .query()

        post = []
        for v in list:
            v['url'] = '/post/' + urllib.quote( str(v['slug']) )
            post.append( v )
        return post





class BlogHandler(core.web.RequestHandler):
    # 配置
    _options = app.model.sys.options()

    def options(self):
        return BlogHandler._options

    def render(self, template_name, **kwargs):
        kwargs['options'] = self._options

        # 读取皮肤目录
        path = 'template/'+ self.options()['site_templates'] +'/'

        # 实例化模板扩展
        kwargs['Q'] = templatePlug(self, path, **kwargs)

        #设置默认模板页面
        if not template_name:
            template_name = 'default.html'

        return self.write(self.render_string(path + template_name, **kwargs))


'''
首页
'''
class index(BlogHandler):
    def get(self):
        try:
            contentModel = app.model.bc.content()
            page = self.get_argument('page',1)
            db = contentModel.find().limitPage( page  , 10)\
                                    .order('[order] DESC , [id] DESC')\
                                    .fields('[id] , [title], [text] , [created] , [slug] , [type]')

            find = self.get_argument('q' , False)
            urlargs = {}

            if False == find:
                db.where('[type] = %s AND [status] = %s' , 'post', 'publish')
            else :
                db.where('[type] = %s AND [status] = %s AND [title] LIKE %s' , 'post', 'publish' ,  '%' + find + '%')
                urlargs['q'] = find

            pagination = db.getPagination()
            contents = db.query()

            if 0 != len(urlargs):
                urlargs = '&' + urllib.urlencode(urlargs)
            else:
                urlargs = ''

            self.render('index.html', list = contents , pagination = pagination , urlargs = urlargs )
        except:
            return self.redirect('/install')

'''
feed
'''
class feed(BlogHandler):
    def get(self):
        self.set_header('Content-Type','application/xml')
        mc = pylibmc.Client()
        feed = mc.get('QcoreBlogFeedXML')

        if feed :
            return self.write( feed )

        contentModel = app.model.bc.content()
        list = contentModel.find('[type] = %s AND [status] = %s' , 'post' , 'publish')\
                           .fields('[id],[title],[slug],[text],[created],[user_id]')\
                           .order('[order] DESC , [id] DESC')\
                           .limit(0 , 10)\
                           .query()

        feed = self.render_string('feed.xml' ,
                                  host = self.request.host ,
                                  options = self._options ,
                                  Q = templatePlug(self, '/', options = self._options ),
                                  time = time.time() ,
                                  list = list )
        mc.set('QcoreBlogFeedXML' , feed , 3600)
        return self.write( feed )

'''
分类
'''
class category(BlogHandler):
    def get(self, name = False ):
        if name :
            name = tornado.escape.url_unescape( name )
            metaModel = app.model.bc.meta()
            page = self.get_argument('page',1)
            db = metaModel.find().limitPage( page  , 10)\
                                 .join('[bc_meta_has_content] ON [bc_meta].[id] = [bc_meta_has_content].[meta_id]')\
                                 .join('[bc_content] ON [bc_meta_has_content].[content_id] = [bc_content].[id]')\
                                 .where('[bc_meta].[name]  = %s AND [bc_content].[status] = %s' , name, 'publish')\
                                 .order('[bc_content].[id] DESC')\
                                 .fields('[bc_content].[id] , [bc_content].[title], '
                                         '[bc_content].[text] , [bc_content].[created] , '
                                         '[bc_content].[slug] , [bc_meta].[name] , [bc_content].[type]')

            pagination = db.getPagination()
            contents = db.query()
            self.render('category.html', list = contents , pagination = pagination , urlargs = '' )
        else:
            self.render('404.html')

'''
tag
'''
class tag(BlogHandler):
    def get(self, name = False ):
        if name :
            name = tornado.escape.url_unescape( name )
            metaModel = app.model.bc.meta()
            page = self.get_argument('page',1)
            db = metaModel.find().limitPage( page  , 10)\
                                .join('[bc_meta_has_content] ON [bc_meta].[id] = [bc_meta_has_content].[meta_id]')\
                                .join('[bc_content] ON [bc_meta_has_content].[content_id] = [bc_content].[id]')\
                                .where('[bc_meta].[name]  = %s AND [bc_content].[status] = %s' , name, 'publish')\
                                .order('[bc_content].[id] DESC')\
                                .fields('[bc_content].[id] , [bc_content].[title], '
                                        '[bc_content].[text] , [bc_content].[created] , '
                                        '[bc_content].[slug] , [bc_meta].[name] , [bc_content].[type]')

            pagination = db.getPagination()
            contents = db.query()
            self.render('tag.html', list = contents , pagination = pagination , urlargs = '' )
        else:
            self.render('404.html')



'''
POST
'''
class post(BlogHandler):
    def get(self , slug = False):
        if False != slug:
            slug = tornado.escape.url_unescape( slug )
            post = app.model.bc.content().find('[slug] = %s AND [type] = %s AND [status] = %s' ,  slug , 'post' , 'publish' ).query()
            if post:
                post['text'] = markdown2.markdown( post['text'] )
                postTags = app.model.bc.content.tags( post['id'] )

                siteComment = self.options()['site_comment'] and self.options()['site_comment'] or {}

                return self.render("post.html" , post=post, postTags=postTags , siteComment=siteComment)

        self.render('404.html')

'''
页面
'''
class page(BlogHandler):
    def get(self , slug = False):
        if False != slug:
            slug = tornado.escape.url_unescape( slug )
            page = app.model.bc.content().find('[slug] = %s AND [type] = %s AND [status] = %s' ,  slug , 'page' , 'publish' ).query()
            if page:
                page['text'] = markdown2.markdown( page['text'] )
                pageTags = app.model.bc.content.tags( page['id'] )
                return self.render("page.html" , page=page, pageTags=pageTags)

        self.render('404.html')






