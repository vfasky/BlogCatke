#coding=utf-8
import functools
from xcat import utils

'''
## 访问控制

特殊标识: 

 - ACL_NO_ROLE 没有角色用户
 - ACL_HAS_ROLE 有角色用户

demo :
    acls = [
        {'URI' : 'app.controllers.default.Login' , 'allow' : ('ACL_NO_ROLE')} ,
        {'URI' : 'app.controllers.admin.*' , 'allow' : ('admin')} ,
        {'URI' : 'app.controllers.*' , 'deny' : ('black')} ,
    ]

'''
def acl(method):

    # 检查
    def check(rule,roles):

        if rule.get('deny',False):
            for r in roles :
                if r in rule['deny'] :
                    return False

        if rule.get('allow',False):
            for r in roles :
                if r in rule['allow'] :
                    return True

        return False



    @functools.wraps(method)
    def wrapper(self, transforms, *args, **kwargs):
        # 唯一标识
        URI  = self.__class__.__module__ + '.' + self.__class__.__name__
        # 访问规则
        rules = self.settings['acls']
        # 当前用户
        current_user = self.current_user


        # 格式化角色
        roles = []
        if None == current_user:
            roles.append('ACL_NO_ROLE')

        elif utils.Validators.is_dict(current_user):
            if False == current_user.has_key('roles') \
               or 0 == len(current_user['roles']):

                roles.append('ACL_NO_ROLE')
            else:
                roles.append('ACL_HAS_ROLE')

                for r in current_user['roles']:
                    roles.append(r)

        for r in rules:
            if r['URI'].find('*') == -1 and r['URI'] == URI :
                if False == check(r,roles) :
                    self._transforms = transforms
                    self.on_access_denied()
                    return self.finish()

            elif URI.find(r['URI'].split('*')[0]) == 0:
                if False == check(r,roles) :
                    self._transforms = transforms
                    self.on_access_denied()
                    return self.finish()

        return method(self, transforms, *args, **kwargs)

    return wrapper
  

class Database(object):
    '''
    数据库
    '''

    # 读标志
    READ  = 'read'
    # 写标志
    WRITE = 'write'

    # 配置
    _setting = False

    # 连接池
    _pool = {}

    @staticmethod
    def load_config(settings):
    	Database._setting = settings

    @staticmethod
    def get_adapter(db_type):
        adapter = Database._pool.get(db_type, False)
      
        if adapter : return adapter
 
        if Database._setting:
            adapter = Database._setting['adapter'] + 'Database'
            import peewee
            if hasattr(peewee,adapter):
                for cfg_type in Database._setting['config']:
                    db_config = Database._setting['config'][cfg_type]
                    database  = db_config.pop('database')
                    if cfg_type == Database.READ or cfg_type == Database.WRITE:
                        Database._pool[cfg_type] = getattr(peewee,adapter)(None)
                        Database._pool[cfg_type].init(database,**db_config)
                    else:
                        db_con = getattr(peewee,adapter)(None)
                        db_con.init(database,**db_config)
                        Database._pool[Database.READ] = db_con
                        Database._pool[Database.WRITE] = db_con
                        break

            
        return Database._pool.get(db_type, False)

    @staticmethod
    def connect(db_type = 'read'):
    	adapter = Database.get_adapter(db_type)

    	if adapter.is_closed() : 
    		adapter.connect()
    		return True
    	return False

    @staticmethod
    def close():
        adapter = Database.get_adapter(Database.WRITE)
        if adapter and False == adapter.is_closed():     
            adapter.close()
        adapter = Database.get_adapter(Database.READ)
        if adapter and False == adapter.is_closed(): 
            adapter.close()

