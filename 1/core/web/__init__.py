#coding=utf-8
__author__ = 'vfasky'

import tornado.escape
import uuid
import time
import core.db
import functools
import tornado.web

from tornado.web import HTTPError
'''
== Session 类 ==
# 每个会话有效期最长为1天
# 在实例化时,可指定ID, 没有指定时,生成一个32位的id

=== API : ===
# session = new Session()
# session.id() # 取 session id
# session.set( key , value )
# session.get( key )
# session.delete( key )
# session.clear() # 清空session

# session[key]
# session[key] = value
# for k in session.keys()
# del session[key]

'''
class Session:

    def __init__(self , session_id = None , store = 'Memcache' , args = {} ):
        if 'MySQL' == store :
            if args.has_key( 'db_name' ) :
                self.store = Session_Store_MySQL( args['db_name'] )
            else:
                self.store = Session_Store_MySQL( 'sys_session')
        elif 'Memcache' == store:
            self.store = Session_Store_Memcache()
        else :
            self.store = Session_Store_StaticClass()

        self.time = 1800
        if session_id :
            self.session_id = session_id
        else :
            self.session_id = self._generate_session_id()

    def _generate_session_id(cls):
        return str(uuid.uuid4())

    # 返回 session id
    def id(self):
        return self.session_id

    # 设置session
    def set(self , key , value):
        self.store.set( self.session_id , key , value , self.time )

    # 取值
    def get(self , key):
        return self.store.get( self.session_id , key )

    # 删除值
    def delete(self , key):
        self.store.delete( self.session_id , key  )

    # 清空
    def clear(self):
        self.store.clear( self.session_id )

    def __getitem__(self, key):
        return self.get( key )

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

# 将session放入 memcache
class Session_Store_Memcache:
    def __init__(self):
        import pylibmc
        self.mc = pylibmc.Client()

    def get(self , session_id , key):
        # print str(session_id)
        data = self.get_data(session_id)
        if not data:
            return None
        if data['values'].has_key( key ):
            return data['values'][key]
        return None

    def clear(self,session_id):
        self.mc.delete( session_id )

    def delete(self ,session_id , key):
        data = self.get_data(session_id)
        if data and data['values'].has_key( key ):
            del data['values'][key]

            session = {
                'values' : data['values'] ,
                'session_time' : int(time.time()) ,
                'left_time' : data['left_time']
            }

            self.mc.set( session_id , tornado.escape.json_encode( session ) , int(data['left_time']) )

    def set(self , session_id , key , value , left_time = 1800):
        data = self.get_data( session_id )
        if not data :
            data = { 'values' : {} }

        data['values'][ key ] = value

        session = {
            'values' : data['values'] ,
            'session_time' : int(time.time()) ,
            'left_time' : int(left_time)
        }

        self.mc.set( session_id , tornado.escape.json_encode( session ) , int(left_time) )

    def get_data(self, session_id):
        data = self.mc.get( session_id )
        if not data :
            return False
        data = tornado.escape.json_decode( data )

        # 超时,删除
        if time.time() > ( data['session_time'] + data['left_time'] ) :
            self.clear( session_id )
            return False

        # 更新时间 , 离结束还有 10 秒, 更新生命周期
        if time.time() > ( data['session_time'] + data['left_time'] - 10 ):
            data['session_time'] = int(time.time())
            self.mc.set( session_id , tornado.escape.json_encode( data ) , int(data['left_time']) )
        return data



# 将session放在表中
class Session_Store_MySQL:

    def __init__(self , db_name):
        db = core.db.base()
        self.db = db.table( db_name )

    def get(self , session_id , key):
        data = self.get_data( session_id )
        if data:
            session = tornado.escape.json_decode( data.session_value )
        else:
            return None

        if time.time() > ( data['session_time'] + data['left_time'] - 10 ):
            # 更新最后访问时间
            self.db.attr = {
                'session_time' : int(time.time())
            }
            self.db.save('[session_key] = %s' , session_id)

        if session.has_key( key ):
            return session[key]
        else:
            return None

    # 取数据
    def get_data(self, session_id):
        data = self.db.find('[session_key] = %s' , session_id).query()
        if not data:
            return False
        
        # 超时,删除
        if time.time() > ( data.session_time + data.session_left_time ) :
            self.clear(session_id)
            return False
        return data

    def set(self , session_id , key , value , left_time = 1800):
        data = self.get_data( session_id )
        if data:
            session = tornado.escape.json_decode( data.session_value )
        else:
            session = {}

        session[ key ] = value
        value = tornado.escape.json_encode( session )

        if not data:
            self.db.attr = {
                'session_key' : session_id ,
                'session_value' : value ,
                'session_left_time' : int(left_time) ,
                'session_time' : int(time.time()) ,
            }
            self.db.add()

        else:
            self.db.attr = {
                'session_value' : value ,
                'session_time' : int(time.time()) ,
            }
            self.db.save('[session_key] = %s' , session_id)


    def clear(self,session_id):
        self.db.delete('[session_key] = %s' , session_id)

    def delete(self ,session_id , key):
        data = self.get_data( session_id )
        if data:
            session = tornado.escape.json_decode( data.session_value )
            if session.has_key( key ):
                del session[key]
                value = tornado.escape.json_encode( session )
                self.db.attr = {
                    'session_value' : value ,
                    'session_time' : int(time.time()) ,
                }
                self.db.save('[session_key] = %s' , session_id)


# 静态对象储存 , 代码reload后失效
class Session_Store_StaticClass:
    _DATA = {}

    def get_session( self ,session_id ):
        if Session_Store_StaticClass._DATA.has_key( session_id ) :
            return Session_Store_StaticClass._DATA[session_id]
        return {}

    def set(self , session_id , key , value , time = 0):
        session = self.get_session( session_id )
        session[ key ] = value
        Session_Store_StaticClass._DATA[ session_id ] = session

    def get(self , session_id , key):
        session = self.get_session( session_id )
        if session.has_key( key ) :
            return session[key]
        return {}

    def delete(self , session_id  , key):
        session = self.get_session( session_id )
        if session.has_key( key ) :
            del session[ key ]
            Session_Store_StaticClass._DATA[ session_id ] = session

    def clear(self , session_id):
        if Session_Store_StaticClass._DATA.has_key( session_id ):
            del Session_Store_StaticClass._DATA[ session_id ]



'''
== 将 Session 加入 RequestHandler ==

=== api ===
# get_session
# set_session

=== 注: ===
# 调用 self._session_Instance() ,可直接访问 self._session
# self._session 支持字典属性
# self._session['key'] , self._session['key'] = 'val'
# for k in self._session.keys()
'''
class RequestHandler(tornado.web.RequestHandler):

    def __init__(self, application, request, **kwargs):
        self._start_time = time.time()
        tornado.web.RequestHandler.__init__(self, application, request, **kwargs)

    # 取session实例
    def session(self):
        # session 已经实例化,直接返回
        if hasattr( self , ' _session' ):
            return self._session

        if self.get_secure_cookie('PYSESSID'):
            self._session = Session( self.get_secure_cookie('PYSESSID') , self.settings['session']['store'] , self.settings['session']['args'] )
        else:
            self._session = Session( False  , self.settings['session']['store'] , self.settings['session']['args']  )
            self.set_secure_cookie( 'PYSESSID' , self._session.id() )

        return self._session

    # 显示错误信息
    def error(self,**args):
        args['url'] = args.has_key('url') and args['url'] or self.request.path
        return self.render("error.html" , **args)


        # 取session值
    def get_session(self , key):
        return self.session().get(key)

    # 设置session值
    def set_session(self , key , val):
        self.session().set(key , val)

    # 访问被拒绝时的错误处理函数
    def _on_access_denied(self):
        self.error( msg = '403 禁止访问' , url= '/login' )
        #raise HTTPError(403)
 
    # 数据库连接
    def db(self):
        return core.db.base()

    # 设置当前用户acl信息
    def set_acl_current_user(self , info , roles = []):
        user_info = info
        user_info['roles'] = roles
        self.session().set('current_user' , user_info)

    # 取当前用户acl信息
    def acl_current_user(self):
        current_user = self.session().get('current_user')
        #print current_user
        if not current_user:
            return {}
        return current_user

    # 清空当前用户acl信息
    def clear_acl_current_user(self):
        self.session().delete('current_user')

    def request_time(self):
        """Returns the amount of time it took for this request to execute."""
        return time.time() - self._start_time

# 实现 ACL 访问控制
def acl(method):

    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        # 取当前用户
        current_user = self.acl_current_user()
        if current_user.has_key('roles'):
            roles = current_user['roles']
        else:
            roles = []

        if len( roles ) == 0:
            roles = [ 'ACL_NO_ROLE' ] # 加入标识, 没有角色用户
        else:
            roles.append('ACL_HAS_ROLE') # 加入标识,有角色用户

        roles.append('ACL_EVERYONE') # 加入标识,所有人

        # 取配置
        config = self.settings['acl']

        uri = self.request.path

        import pylibmc
        mc = pylibmc.Client()
        ruleCache = mc.get('ACL_URI_' + uri)
        if not ruleCache:
            # 初始化db
            db = self.db().table( config['db_name'] )
            rule = db.find('[uri] = %s' , uri).query()
            if rule :
                mc.set('ACL_URI_' + uri , tornado.escape.json_encode( rule ))
        else:
            rule = tornado.escape.json_decode( ruleCache )

        from core.web import validators

        # 没有规则,取默认规则
        if not rule:
            default_rule = config['default']
            # 先判断禁止
            if default_rule.has_key('deny'):
                for role in roles:
                    for c_role in default_rule['deny']:
                        if( role == c_role ):
                            return self._on_access_denied()

            # 如果没有定义容许通过的规则,默认是通过
            is_passing = True
            # 判断容许通过
            if default_rule.has_key('allow'):
                is_passing = False
                for role in roles:
                    for c_role in default_rule['allow']:
                        if( role == c_role ):
                            is_passing = True
                            break

            if False == is_passing:
                return self._on_access_denied()

        # 规则存在 , 检查规则
        else:
            # 先判断禁止
            if rule['deny'] != None and rule['deny'] != '':
                rule['deny'] = tornado.escape.json_decode( rule['deny'] )
                if validators.IsList( rule['deny'] ) :
                    for role in roles:
                        for c_role in rule['deny']:
                            if( role == c_role ):
                                return self._on_access_denied()

            # 如果没有定义容许通过的规则,默认是通过
            is_passing = True
            # 判断容许通过
            if rule['allow'] != None and rule['allow'] != '':
                rule['allow'] = tornado.escape.json_decode( rule['allow'] )
                is_passing = False
                if validators.IsList( rule['allow'] ) :
                    for role in roles:
                        for c_role in rule['allow']:
                            if( role == c_role ):
                                is_passing = True
                                break

            if False == is_passing:
                return self._on_access_denied()

        return method(self, *args, **kwargs)
    return wrapper


