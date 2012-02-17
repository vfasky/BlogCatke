#coding=utf-8
__author__ = 'vfasky'

from core import db
from core.web import validators
import app.model.uc
import tornado.escape
import pylibmc



'''
配置表
'''
class options(db.base):

    def __init__(self):
        db.base.__init__(self)
        self.db_name = 'sys_options'
        self._options = {}

    '''
   系统设置
   '''
    def __setitem__(self, key, value):
        key = key.strip()
        json = tornado.escape.json_encode( value )
        # 添加
        if 0 == self.find('[name] = %s AND [user_id] = 0' , key ).count():

            self.attr = {
                'user_id' : 0 ,
                'name' : key ,
                'value' : json ,
            }
            self.add()
        else :
            self.attr = {
                'value' : json ,
            }
            self.save('[name] = %s AND [user_id] = 0' , key )

        self._options[ key ] = value

    def __delitem__(self, item):
        key = item.strip()
        self.delete('[name] = %s AND [user_id] = 0' , key)
        if key in self._options:
            del self._options[key]

    def __getitem__(self, item):
        key = item.strip()

        if self._options.has_key( key ):
            return self._options[ key ]

        data = self.find('[name] = %s AND [user_id] = 0' , key ).query()
        if not data:
            self._options[ key ] = None
            return None
        value = tornado.escape.json_decode( data['value'] )
        self._options[ key ] = value
        return value

'''
插件
'''
class plugin(db.base):

    def __init__(self):
        self._mc = pylibmc.Client()
        self._option = options()

    @classmethod
    def getInstantiate(cls,name):
        pluginName = 'app.plugin.' + name.strip()
        import sys
        __import__( pluginName )
        return getattr( sys.modules['app.plugin.' + name] , name )()

    # 取激活的插件列表
    def getList(self):
        if None == self._option['plugin_list']:
            self._option['plugin_list'] = []
        return self._option['plugin_list']

    # 取激活的插件列表,并格式化成相应的格式
    def list(self):


        # 从mc中取
        pluginList = self._mc.get('_QcoreBlog.plugin.list')

        if pluginList :
            plugin._list = pluginList
            return pluginList

        pluginList = {
            'beforeExecute' : {} ,
            'beforeRender' : {} ,
            'afterExecute' : {} ,
        }

        list = self.getList()

        for name in list:
            interfaces = self.getInterface(name)
            for cfg in interfaces:
                if False == pluginList[ cfg['type'] ].has_key( cfg['target'] ):
                    pluginList[ cfg['type'] ][ cfg['target'] ] = []
                pluginList[ cfg['type'] ][ cfg['target'] ].append( { 'name' : name , 'action' : cfg['action'] } )

        # 写入mc中
        self._mc.set('_QcoreBlog.plugin.list' , pluginList)

        return pluginList

    # 添加插件
    def add(self , name ,**args):
        list = self.getList()
        if name not in list :
            list.append( name )
            self._option['plugin_list'] = list
            self.setData( name , **args )
            # 清缓存
            self._mc.set('_QcoreBlog.plugin.list',False)
            self.list()


    # 移除插件
    def remove(self,name):
        list = self.getList()
        if name in list:
            self.delData( name )
            del list[ list.index(name) ]
            self._option['plugin_list'] = list
            # 清缓存
            self._mc.set('_QcoreBlog.plugin.list',False)
            self.list()


    def getData(self,name):
        key = 'plugin:' + name.strip()
        return self._option[ key ]

    def delData(self,name):
        key = 'plugin:' + name.strip()
        del self._option[ key ]

    def setData(self,name,**args):
        key = 'plugin:' + name.strip()

        args['config'] = args.has_key('config') and args['config'] or {}
        args['interface'] = args.has_key('interface') and args['interface'] or []

        self._option[ key ] = args

    def _getData(self,name,key):
        data = self.getData(name)
        if data and data.has_key( key ):
            return data[ key ]
        return {}

    def getConfig(self,name):
        return self._getData(name,'config')

    def getInterface(self,name):
        return self._getData(name,'interface')

    def getDesc(self,name):
        return self._getData(name,'desc')



'''
权限控制表
'''
class acl(db.base):

    def __init__(self):
        db.base.__init__(self)
        self.db_name = 'sys_acl'

    # 取角色列表
    @classmethod
    def getRoles(cls):
        roles = app.model.uc.role().find().getAll()

        rolesData = []
        for role in roles:
            rolesData.append( { 'label' : role['name'] , 'value' : role['code'] } )
        rolesData.append( { 'label' : '*没有角色用户' , 'value' : 'ACL_NO_ROLE' } )
        rolesData.append( { 'label' : '*有角色用户' , 'value' : 'ACL_HAS_ROLE' } )
        rolesData.append( { 'label' : '*所有人' , 'value' : 'ACL_EVERYONE' } )

        return rolesData

    #更改角色code
    @classmethod
    def editRoleCode(cls , code , newCode = False):
        acls = cls().find().getAll()
        for acl in acls:
            if False != newCode : #更改
                if validators.NotEmpty( acl['deny'] ):
                    acl['deny'] = acl['deny'].replace('"'+code+'"' , '"'+newCode+'"' )
                if validators.NotEmpty( acl['allow'] ):
                    acl['allow'] = acl['allow'].replace('"'+code+'"' , '"'+newCode+'"' )
            else: #删除
                if validators.NotEmpty(acl['deny']) :
                    acl['deny'] = tornado.escape.json_decode( acl['deny'] )
                    if False == validators.IsList( acl['deny'] ):
                        if validators.IsString(acl['deny']):
                            acl['deny'] = acl['deny'].replace('"'+code+'"' , '' )
                    else:
                        for k in acl['deny']:
                            if k == code :
                                acl['deny'].remove( k )

                                break
                    acl['deny'] = tornado.escape.json_encode( acl['deny'] )

                if validators.NotEmpty(acl['allow']) :
                    acl['allow'] = tornado.escape.json_decode( acl['allow'] )
                    if False == validators.IsList( acl['allow'] ):
                        if validators.IsString(acl['allow']):
                            acl['allow'] = acl['allow'].replace('"'+code+'"' , '' )
                    else:
                        for k in acl['allow']:
                            if k == code :
                                acl['allow'].remove( k )
                                break
                    acl['allow'] = tornado.escape.json_encode( acl['allow'] )

            model = cls()
            model.attr = {
                'allow' : acl['allow'] ,
                'deny' : acl['deny'],
            }
            model.save('[id] = %s' , acl['id'])


    # 格式化角色
    @classmethod
    def rolesDecode(cls , roleJson):
        if not roleJson:
            return ''
        roles = tornado.escape.json_decode( roleJson )
        if not roles:
            return ''

        if False == validators.IsList( roles ):
            roles = [ roles ]

        rolesData = cls.getRoles()
        ret = []
        for role in roles:
            for v in rolesData:
                if v['value'] == role :
                    ret.append( v['label'] )

        return ','.join( ret )
