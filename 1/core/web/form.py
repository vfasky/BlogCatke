#coding=utf-8
__author__ = 'vfasky'

import core.web.validators
import tornado.escape

class Form:
    def __init__(self):
        self.items = []
        self.values = {}
        self.msg = ''

    def add(self , itemObj):
        self.items.append( itemObj )

    def toJson(self):
        data = []

        for item in self.items:
            data.append( item.toDict() )

        return tornado.escape.json_encode( data )

    def validators(self , values):
        for k in values:
            for item in self.items:
                if item.name == k:
                    item.setValue( values[k] )

        for item in self.items:

            ret = item.check()

            if ret['success']:
                self.values[ item.name ] = item.getValue()
            else:
                self.msg = ret['msg']
                return False

        return True

'''
表单验证
'''
class Validators:
    @staticmethod
    def notEmpty(value,label):
        if core.web.validators.NotEmpty( value ):
            return { 'success' : True }
        return { 'success' : False , 'msg' : label + '不能为空' }

    @staticmethod
    def isNumber(value,label):
        if core.web.validators.IsNumber( value ):
            return { 'success' : True }
        return { 'success' : False , 'msg' : label + '只能为数字' }

    @staticmethod
    def isEmail(value,label):
        if core.web.validators.IsEmail( value ):
            return { 'success' : True }
        return { 'success' : False , 'msg' : label + '的邮箱格式错误' }



'''
表单组件基类
'''
class itemBase:
    def __init__(self, name, *validators, **attrs):
        self.name = name
        self.validators = validators
        self.attrs = attrs
        self.value = self.attrs.pop('value', None)
        self.label = self.attrs.pop('label', None)

    def setValue(self, value):
        if len(value) == 1 :
            self.value = value[0]
        else :
            self.value = value

    def getValue(self):
        return self.value

    def getAttr(self):
        return self.attrs

    def toDict(self):
        return {
            'label' : self.label ,
            'name' : self.name ,
            'type' : self.type ,
            'value': self.value ,
            'attrs' : self.attrs ,
            'validators' : self.validators
        }

    def check(self):
        for v in self.validators :
            if hasattr( Validators , v ):
                label = self.label
                if None == label:
                    label = self.name
                ret = getattr( Validators , v )( self.value , label )

                if False == ret['success']:
                    return ret

        return { 'success' : True }

class Hidden(itemBase):
    def __init__(self, name, *validators, **attrs):
        self.type = 'hidden'
        itemBase.__init__(self, name, *validators, **attrs)

# 下拉框
class Select(itemBase):
    def __init__(self, name, *validators, **attrs):
        self.type = 'select'
        itemBase.__init__(self, name, *validators, **attrs)
        self.data = self.attrs.pop('data', None)


    def setValue(self, value):
        for item in self.data:
            for v in value:
                if v == str(item['value']) :
                    self.value = v
                    return

    def toDict(self):
        return {
            'label' : self.label ,
            'name' : self.name ,
            'type' : self.type ,
            'value': self.value ,
            'attrs' : self.attrs ,
            'validators' : self.validators ,
            'data' : self.data
        }

# 多选框
class Checkbox(itemBase):
    def __init__(self, name, *validators, **attrs):
        self.type = 'checkbox'
        itemBase.__init__(self, name, *validators, **attrs)
        self.data = self.attrs.pop('data', None)
        self.value = self.attrs.pop('value', [])

    def setValue(self, value):
        for item in self.data:
            for v in value:
                if str(item['value']) == v :
                    self.value.append( v )


    def toDict(self):
        return {
            'label' : self.label ,
            'name' : self.name ,
            'type' : self.type ,
            'value': self.value ,
            'attrs' : self.attrs ,
            'validators' : self.validators ,
            'data' : self.data
        }

class Input(itemBase):
    def __init__(self, name, *validators, **attrs):
        self.type = 'text'
        itemBase.__init__(self, name, *validators, **attrs)

class Password(itemBase):
    def __init__(self, name, *validators, **attrs):
        self.type = 'password'
        itemBase.__init__(self, name, *validators, **attrs)

class Textarea(itemBase):
    def __init__(self, name, *validators, **attrs):
        self.type = 'textarea'
        itemBase.__init__(self, name, *validators, **attrs)



