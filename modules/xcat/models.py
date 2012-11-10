#coding=utf-8
from peewee import *
from xcat import Database 

Model._meta.database = Database.get_adapter(Database.READ)

class Model(Model):
    """
    基础模型
    """
    class Meta:
        database = Database.get_adapter(Database.READ)

    @classmethod
    def raw(cls, sql, *params):
        cls._meta.database = Database.get_adapter(Database.READ)
        return super(Model,cls).raw(sql, *params)

    @classmethod
    def select(cls, *selection):
        cls._meta.database = Database.get_adapter(Database.READ)
        return super(Model,cls).select(*selection)

    @classmethod
    def update(cls, **update):
        cls._meta.database = Database.get_adapter(Database.WRITE)
        return super(Model,cls).update(**update)

    @classmethod
    def insert(cls, **insert):
        cls._meta.database = Database.get_adapter(Database.WRITE)
        return super(Model,cls).insert(**insert)

    @classmethod
    def delete(cls):
        cls._meta.database = Database.get_adapter(Database.WRITE)
        return super(Model,cls).delete()

    @classmethod
    def create(cls, **query):
        cls._meta.database = Database.get_adapter(Database.WRITE)
        return super(Model,cls).create(**query)

    @classmethod
    def create_table(cls, fail_silently=False):
        cls._meta.database = Database.get_adapter(Database.WRITE)
        return super(Model,cls).create_table(fail_silently)

    @classmethod
    def drop_table(cls, fail_silently=False):
        cls._meta.database = Database.get_adapter(Database.WRITE)
        return super(Model,cls).drop_table(fail_silently)

    def save(self, force_insert=False):
        self._meta.database = Database.get_adapter(Database.WRITE)
        return super(Model,self).save(force_insert)

class Session(Model):
    '''
    session 
    '''
    id        = CharField(max_length=64,primary_key=True)
    user_id   = IntegerField()
    time_out  = IntegerField()
    left_time = IntegerField()
    values    = TextField()

class Plugins(Model):
    """
    插件
    """
    name        = CharField(max_length=100,unique=True)
    bind        = TextField()
    handlers    = TextField(default='[]') # 控制器
    ui_modules  = TextField(default='[]') # ui_modules
    config      = TextField(default='{}') # 配置
 
