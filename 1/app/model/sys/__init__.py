#coding=utf-8
__author__ = 'vfasky'

from core import db
from core.web import validators
import app.model.uc
import tornado.escape

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
