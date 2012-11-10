#coding=utf-8
import uuid , os
import time
import peewee
import xcat
import xcat.utils as utils
from tornado.util import import_object

class Base(object):
    """session 基类"""

    _data = {}

    @staticmethod
    def get_data(session_id, storage=False):
        try:    
            data = storage.__class__._data.get('__SESSION__' + session_id,False)

            if data and data.has_key('__time__') :
                this_time = int(time.time())
                interval  = this_time - data['__time__']

                if data['__left_time__'] - interval <= 0 :
                    storage.__class__.delete_data(session_id,storage)
                    return {}

                # 维持生命周期
                if data['__left_time__'] - interval < data['__left_time__'] / 2 :
                    storage.__class__.set_data(session_id, data, data['__left_time__'],storage)

            return data and data or {}
        except Exception, e:
            return {}

    @staticmethod
    def set_data(session_id , data , left_time = 1800, storage=False):
        data['__time__']      = int(time.time())
        data['__left_time__'] = int(left_time)
        storage.__class__._data['__SESSION__' + session_id ] = data

    @staticmethod
    def delete_data(session_id, storage=False):
        if storage.__class__._data.has_key('__SESSION__' + session_id):
            del storage.__class__._data['__SESSION__' + session_id]


    def __init__(self, session_id = False, left_time = 1800, settings = {}):
        if False == session_id:
            session_id = str(uuid.uuid4())

        self.session_id = session_id
        self.left_time  = int(left_time)
        self.data       = self.__class__.get_data(self.session_id,self)

    # 返回 session id
    def id(self):
        return self.session_id

    # 设置session
    def set(self , key , value):
        self.data[key] = value
        self.__class__.set_data(self.session_id, self.data, self.left_time, self)

    # 取值
    def get(self , key):
        if self.data.has_key(key):
            return self.data[key]
        return None

    # 删除值
    def delete(self , key):
        if self.data.has_key(key):
            del self.data[key]
            self.__class__.set_data(self.session_id, self.data, self.left_time, self)

    # 清空
    def clear(self):
        self.data = {}
        self.__class__.delete_data(self.session_id,self)

    def __getitem__(self, key):
        return self.get(key)

    def __setitem__(self, key, value):
        return self.set(key , value)

    def __delitem__(self, key):
        return self.delete(key)

    def __len__(self):
        return len(self.data.keys())

    def __str__(self):
        return self.data

    def keys(self):
        return self.data.keys()
        

class Memory(Base):
    """基于内存的session"""

    def __init__(self, session_id = False, left_time = 1800, settings = {}):
        Base.__init__(self, session_id, left_time, settings)

           

class DB(Base):
    """基于数据库的session"""

    # 是否检查表已经存在
    _is_check_table = False

    
    @staticmethod
    def get_data(session_id, storage=False):
        # 检查表是否存在，不存在创建
        if False == storage.__class__._is_check_table :
            if False == storage.model.table_exists():
                storage.model.create_table()
            storage.__class__._is_check_table = True

       
        this_time = int(time.time())
        count     = storage.model.filter(storage.model.id == session_id).count()

        # 表中有 session 信息
        if count > 0:
            try:
                data = storage.model.get(storage.model.id == session_id)
            except Exception, e:
                return {}
    
            # 已经过期，删除
            if data.time_out < this_time :
                storage.model.delete().where(storage.model.id == session_id).execute()
                return {}

            # 如果超过生成周期的一半，维持生命周期
            if int(data.time_out) - this_time < int(data.left_time) / 2:
                
                storage.model\
                       .update(time_out = this_time + int(data.left_time))\
                       .where(storage.model.id == session_id)\
                       .execute()
               
            # 格式化 session 信息           
            session = utils.Json.decode(data.values, {})

            # 退出其它用户
            if session.get('current_user' , False) :
                user_id = session['current_user'].get('user_id' , False)
                if user_id:
                    storage.model.delete().where(storage.model.id != session_id)\
                                          .where(storage.model.user_id == user_id)\
                                          .execute()
                    
            return session

        return {}

    @staticmethod
    def set_data(session_id , data , left_time = 1800 , storage=False):
        
        this_time = int(time.time())
        user_id   = 0
        if data.get('current_user' , False) :
            if data['current_user'].get('user_id' , False) :
                user_id = data['current_user']['user_id']

        
        if 0 == storage.model.filter(storage.model.id == session_id).count() :
            storage.model.insert(
                time_out  = this_time + int(left_time) ,
                left_time = left_time ,
                user_id   = user_id ,
                id        = session_id ,
                values    = utils.Json.encode(data)
            ).execute()
            
        else:
            storage.model.update(
                time_out  = this_time + int(left_time) ,
                left_time = left_time ,
                user_id   = user_id ,
                values    = utils.Json.encode(data)
            ).where(storage.model.id == session_id).execute()
         
    @staticmethod
    def delete_data(session_id, storage=False):
        storage.model.delete().where(storage.model.id == session_id).execute()


    def __init__(self, session_id = False, left_time = 1800, settings = {}):
        self.model = import_object(settings.get('model'))
        Base.__init__(self, session_id, left_time, settings)


if 'SERVER_SOFTWARE' in os.environ:
    import pylibmc

    class SaePylibmc(Base):
        """基于mc的session"""

        mc = pylibmc.Client()

        @staticmethod
        def get_data(session_id, storage=False):
            return storage.mc.get(session_id) or {}

        @staticmethod
        def set_data(session_id , data , left_time = 1800 , storage=False):
            return storage.mc.set(session_id,data)

        @staticmethod
        def delete_data(session_id, storage=False):
            return storage.delete(session_id)

        def __init__(self, session_id = False, left_time = 1800, settings = {}):
            Base.__init__(self, session_id, left_time, settings)