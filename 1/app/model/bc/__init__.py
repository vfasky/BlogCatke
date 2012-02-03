#coding=utf-8
__author__ = 'vfasky'

from core import db
from core.web import validators
import tornado.escape
'''
文章元
'''
class meta(db.base):

    def __init__(self):
        db.base.__init__(self)
        self.db_name = 'bc_meta'

    # 更新总数
    def updateCount(self , list):
        metaHasContentModel = metaHasContent()
        for v in list:
            self.attr = {}
            self.attr['count'] = metaHasContentModel.find('[meta_id] = %s' , v['meta_id']).count()
            self.save('[id] = %s' , v['meta_id'])

    # 删除tag
    def tagDelete(self , id):
        id = int(id)

        # 删除关联
        metaHasContentModel = metaHasContent()
        metaHasContentModel.delete('[meta_id] = %s' , id)
        self.delete('[id] = %s' , id)

    # 删除分类
    def categoryDelete(self , id):
        id = int(id)
        # 查关联
        metaHasContentModel = metaHasContent()
        data = metaHasContentModel.find('[meta_id] = %s' , id).getAll()
        contentIds = []

        for v in data:
            contentIds.append( str(v['content_id']) )

        count = len(contentIds)

        # 删除对应的文章
        if count > 0:
            contentModel = content()
            contentModel.delete('[id] IN ( ' + ','.join( contentIds ) + ' )' )

        # 删除关联
        metaHasContentModel.delete('[meta_id] = %s' , id)
        self.delete('[id] = %s' , id)



class metaHasContent(db.base):
    def __init__(self):
        db.base.__init__(self)
        self.db_name = 'bc_meta_has_content'

'''
内容表
'''
class content(db.base):

    def __init__(self):
        db.base.__init__(self)
        self.db_name = 'bc_content'

    # 只显示简单描述
    @classmethod
    def getDescription(cls,text):
        text = str(text)
        list = text.split('<!--more-->')
        return list[0]

    # 删除文章
    @classmethod
    def remove(cls,contentId):
        contentId = int(contentId)

        metaHasContentModel = metaHasContent()

        # 取关联
        list = metaHasContentModel.find('[content_id] = %s' , contentId).fields('[meta_id]').getAll()


        # 删除文章元关联
        metaHasContentModel.delete('[content_id] = %s' , contentId)
        cls().delete('[id] = %s' , contentId)
        meta().updateCount(list)

    # 删除文章分类
    @classmethod
    def categoryDelete(cls,contentId):
        # 取关联
        list = metaHasContent().find('[content_id] = %s' , int( contentId ) ).fields('[meta_id]').getAll()

        cls().execute('DELETE [bc_meta_has_content].* FROM [bc_meta_has_content] '
                      'Inner Join [bc_content] ON [bc_meta_has_content].[content_id] = [bc_content].[id] '
                      'Inner Join [bc_meta] ON [bc_meta_has_content].[meta_id] = [bc_meta].[id] '
                      'WHERE '
                      '([bc_meta].[type] = %s) AND ( [bc_content].[id] = %s )' , 'category' , int( contentId ))

        meta().updateCount(list)

    # 删除tag
    @classmethod
    def tagDelete(cls,contentId):
        # 取关联
        list = metaHasContent().find('[content_id] = %s' , int( contentId ) ).fields('[meta_id]').getAll()

        cls().execute('DELETE [bc_meta_has_content].* FROM [bc_meta_has_content] '
                      'Inner Join [bc_content] ON [bc_meta_has_content].[content_id] = [bc_content].[id] '
                      'Inner Join [bc_meta] ON [bc_meta_has_content].[meta_id] = [bc_meta].[id] '
                      'WHERE '
                      '([bc_meta].[type] = %s) AND ( [bc_content].[id] = %s )' , 'tag' , int( contentId ))

        meta().updateCount(list)

    # 添加tag关联
    @classmethod
    def tagAdd(cls, tags , contentId):
        if 0 == cls().find('[id] = %s' , contentId).count():
            return False

        metaModel = meta()
        metaHasContentModel = metaHasContent()
        if validators.NotEmpty( tags ):
            tags = tornado.escape.json_decode( tags )
            for tag in tags :
                name = tag.strip()
                data = metaModel.find('[name] = %s AND [type] = %s' , name , 'tag').fields('[id]').query()
                # 添加
                if not data:
                    metaModel.attr = { 'name' : name , 'type' : 'tag' }
                    id = metaModel.add()

                else:
                    id = data['id']

                metaHasContentModel.attr = {
                    'content_id' : contentId ,
                    'meta_id' : id ,
                }
                metaHasContentModel.add()

                metaModel.updateCount([{ 'meta_id' : id }])
        return True

    @classmethod
    def tags(cls , contentId):
        ret = cls().query('SELECT [bc_meta].[id] , [bc_meta].[name] '
                          'FROM [bc_content] '
                          'Inner Join [bc_meta_has_content] ON [bc_content].[id] = [bc_meta_has_content].[content_id] '
                          'Inner Join [bc_meta] ON [bc_meta_has_content].[meta_id] = [bc_meta].[id] '
                          'WHERE '
                          '([bc_meta].[type] = %s) AND ( [bc_content].[id] = %s ) ' , 'tag' , int( contentId ))
        return ret

    # 取文章分类
    @classmethod
    def category(cls , contentId):
        ret = cls().get('SELECT [bc_meta].[id] , [bc_meta].[name] '
                        'FROM [bc_content] '
                        'Inner Join [bc_meta_has_content] ON [bc_content].[id] = [bc_meta_has_content].[content_id] '
                        'Inner Join [bc_meta] ON [bc_meta_has_content].[meta_id] = [bc_meta].[id] '
                        'WHERE '
                        '([bc_meta].[type] = %s) AND ( [bc_content].[id] = %s ) ' , 'category' , int( contentId ))


        return ret