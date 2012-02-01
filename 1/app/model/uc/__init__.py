#coding=utf-8
__author__ = 'vfasky'

from core import db

'''
会员部分
'''
class user(db.base):

    def __init__(self):
        db.base.__init__(self)
        self.db_name = 'uc_user'

    # 绑定角色
    @classmethod
    def bindRoles(cls,id,roleIds):
        # 先删除旧数据
        roleHasRoleModel = db.base().table('uc_role_has_user')
        roleHasRoleModel.delete('[user_id] = %s' , int(id))

        for roleId in roleIds:
            if 1 == role().find('[id] = %s' , int(roleId)).count():
                roleHasRoleModel.attr = {
                    'user_id' : int(id) ,
                    'role_id' : int(roleId)
                }
                roleHasRoleModel.add()


    # 取角色列表
    @classmethod
    def roleList(cls,id):
        model = cls()
        list = model.query( 'SELECT [uc_role].[id],[uc_role].[code],[uc_role].[name] FROM [uc_user] '
                            'Inner Join [uc_role_has_user] ON [uc_user].[id] = [uc_role_has_user].[user_id] '
                            'Inner Join [uc_role] ON [uc_role_has_user].[role_id] = [uc_role].[id] '
                            'WHERE [uc_user].[id] = %s' , int(id) )
        return list

    # 取角色代码
    @classmethod
    def roleCodes(cls,id):
        code = []
        for role in cls.roleList(id):
            code.append( role['code'] )
        return code

    # 取角色Id
    @classmethod
    def roleIds(cls,id):
        ids = []
        for role in cls.roleList(id):
            ids.append( role['id'] )
        return ids

    # 取用户角色名称
    @classmethod
    def roleNamesToStr(cls,id):
        name = []
        for role in cls.roleList(id):
            name.append( role['name'] )

        return ','.join( name )

    # 生成4位随机码
    @classmethod
    def buildEncryption(cls):
        import random
        return ''.join( random.sample('qwertyuiopasdfghjkl;zxcvbnm,./?QWERTYUIOPASDFGHJKLZXCVBNM!@#$%^&*()123456789+-',4) )

'''
角色表
'''
class role(db.base):

    def __init__(self):
        db.base.__init__(self)
        self.db_name = 'uc_role'

    # 编辑数据
    def edit(self,query,*parameters ):
        #原数据
        role = self.find(query,*parameters).query()
        self.save(query,*parameters )
        newRole = self.find(query,*parameters).query()
        if role['code'] != newRole['code'] :
            import app.model.sys
            app.model.sys.acl.editRoleCode(role['code'] , newRole['code'])
        return


    # 关联删除角色
    def remove(self , id):
        role = self.find('[id] = %s' , int(id)).query()
        if not role :
            return

        roleHasUser = db.base().table('uc_role_has_user')
        roleHasUser.delete('[role_id] = %s' , int(id))
        # 删除
        import app.model.sys
        app.model.sys.acl.editRoleCode(role['code'])
        return self.delete('[id] = %s' , int(id))

