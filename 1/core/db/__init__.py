#coding=utf-8
__author__ = 'vfasky'

import tornado.database
import sae.const

class Finder:
    # 将数据库连接放入静态属性 , 使用从库查询
    _db = False

    # 以静态对象的方式,返回唯一的数据库连接
    @staticmethod
    def dbConnection():
        if not Finder._db:
            Finder._db = tornado.database.Connection(
                host= sae.const.MYSQL_HOST_S + ':' + sae.const.MYSQL_PORT, database= sae.const.MYSQL_DB ,
                user= sae.const.MYSQL_USER , password = sae.const.MYSQL_PASS  , max_idle_time = 5 )
        return Finder._db

    def __init__(self , dbName):
        self._where = None
        self._order = None
        self._limit = 1
        self._skip  = 0
        self._page  = 1
        self._pageSize = 20
        self._fields = '*'
        self._join = None
        self.db = Finder.dbConnection()
        self.dbName = dbName

    # 将 [ , ] 转换成 `
    @staticmethod
    def sqlStr(query):
        query = str(query)
        query = query.replace('[' , '`')
        query = query.replace(']' , '`')
        return query

    # Inner Join
    def join(self , sql ):
        if None == self._join:
            self._join = []
        self._join.append( ' Inner Join ' + self.sqlStr( sql ) )
        return self

    # Left Join
    def leftJoin(self , sql ):
        if None == self._join:
            self._join = []
        self._join.append( ' Left Join ' + self.sqlStr( sql ) )
        return self

    # Right Join
    def rightJoin(self , sql ):
        if None == self._join:
            self._join = []
        self._join.append( ' Right Join ' + self.sqlStr( sql ) )
        return self

    # 执行查询,并返回结果
    def query(self):
        sql = 'SELECT ' + self._fields + ' FROM `' + self.dbName + '` '

        if None != self._join :
            for join in self._join :
                sql += join

        parameters = []
        if None != self._where :
            sql += ' WHERE ' + self._where['where']
            parameters = self._where['value']

        if None != self._order :
            sql += ' ORDER BY ' + self._order

        sql += ' LIMIT ' + str(self._skip) + ' , ' + str(self._limit)

        if self._limit == 1 :
            return self.db.get( sql , *parameters )
        return self.db.query( sql , *parameters )

    # 取所有结果
    def getAll(self):
        sql = 'SELECT ' + self._fields + ' FROM `' + self.dbName + '` '

        if None != self._join :
            for join in self._join :
                sql += join

        parameters = []
        if None != self._where :
            sql += ' WHERE ' + self._where['where']
            parameters = self._where['value']

        if None != self._order :
            sql += ' ORDER BY ' + self._order

        return self.db.query( sql , *parameters )

    # 统计查询结果
    def count(self):
        parameters = []
        sql = 'SELECT COUNT(*) AS row_count FROM `' + self.dbName + '`'

        if None != self._join :
            for join in self._join :
                sql += join

        if None != self._where :
            sql += ' WHERE ( ' + self._where['where'] + ' ) '
            parameters = self._where['value']



        ret = self.db.get( sql , *parameters )
        return ret['row_count']

    # 查询条件
    def where(self, where , *value):
        self._where = {
            'where' : Finder.sqlStr( where ) ,
            'value' : value
        }
        return self

    # 排序
    def order(self, order):
        self._order = Finder.sqlStr( order )
        return self

    # 分页查询
    def limitPage(self, page = 1, pageSize = 10):
        self._page = int( page )
        self._pageSize = int( pageSize )
        if self._page <= 0:
            self._page = 1
        return self.limit( ( self._page - 1 ) * self._pageSize , self._pageSize )

    # 取分页信息
    def getPagination(self):
        import math
        #总数量
        count = self.count()

        #总页数
        countPage =  math.ceil( float( count ) / float( self._pageSize ) )

        #前一页
        if self._page <= 1 :
            prev = 1
        else:
            prev = self._page -1
            #下一页
        if self._page < countPage:
            next = self._page + 1
        else:
            next = countPage

        return {
            'prev' : int( prev ) ,
            'next' : int( next ) ,
            'current' : self._page ,
            'countPage' : int( countPage ),
            'count' : int( count )
        }

    # limit
    def limit(self , skip , limit):
        self._limit = int( limit )
        self._skip  = int( skip )
        return self

    # 要查询的字段
    def fields(self,fields):
        self._fields = Finder.sqlStr( fields )
        return self

'''
数据查询基类
'''
class base:
    # 将数据库连接放入静态属性
    _db = False

    # 以静态对象的方式,返回唯一的数据库连接
    @staticmethod
    def dbConnection():
        if not base._db:
            base._db = tornado.database.Connection(
                host= sae.const.MYSQL_HOST + ':' + sae.const.MYSQL_PORT, database= sae.const.MYSQL_DB ,
                user= sae.const.MYSQL_USER , password = sae.const.MYSQL_PASS  , max_idle_time = 5 )
        return base._db

    def __init__(self):
        self.db = base.dbConnection()
        self.table( self.__class__.__name__ )
        self.attr = {}

    '''
    === 实现链接口 ===
    '''
    def table(self , name):
        if 'base' != name:
            self.db_name = name
        return self

    '''
    === 返回查询接口 ===
    '''
    def find(self,query = None,*parameters):
        finder = Finder( self.db_name )
        if None == query:
            return finder
        else:
            return finder.where(query,*parameters)

    '''
    === 删除数据 ===
    # 会删除所有合适条件的数据
    '''
    def delete(self,query,*parameters):
        query =  self.sqlStr(query)
        return self.db.execute('DELETE FROM `'+ self.db_name +'` WHERE ' + query , *parameters )

    # 将 [ , ] 转换成 `
    def sqlStr(self,query):
        return Finder.sqlStr( query )

    # 复杂查询, 只转换[ ]
    def query(self,query,*parameters):
        return self.db.query(self.sqlStr(query) , *parameters )

    # 复杂查询, 只转换[ ] , 一条数据
    def get(self,query,*parameters):
        return self.db.get(self.sqlStr(query) , *parameters )

    # 写入 或 修改 值时传递的参数
    def __setitem__(self , key , val):
        self.attr[ key ] = val

    # 取设置的参数
    def __getitem__(self, key):
        if self.attr.has_key( key ):
            return self.attr[key]
        return None
    
    # 删除参数
    def __delitem__(self, key):
        if self.attr.has_key( key ):
            del self.attr[key]

    # 清除参数
    def clearAttr(self):
        self.attr = {}

    # 执行sql语句
    def execute(self , sql , *parameters):
        return self.db.execute(  self.sqlStr( sql )  , *parameters )

    '''
    === 写入数据 ===
    # demo :
    m = model.base().table('mv_actor')
    m['name'] = 'test'
    m['create_time'] = '0'
    m.add()
    '''
    def add(self):
        if len( self.attr) == 0 :
            return False

        #INSERT INTO "+ self.db_name +" ( `session_key`,`session_value`,`session_left_time`,`session_time`) VALUES ( %s,%s,%s,%s)
        parameters = []
        key = []
        str = []
        sql = 'INSERT INTO `'+ self.db_name +'` '

        #print self.attr
        for k in self.attr.keys():
            key.append( '`' + k + '`' )
            str.append( '%s')
            parameters.append( self.attr[ k ] )

        sql = sql + '(' + ','.join(key) + ') VALUES (' + ','.join(str) + ')'

        return self.db.execute( sql , *parameters )

  

    '''
    === 保存数据 ===
    # 注:只能操作单条数据,批量处理请使用 execute 方法
    '''
    def save(self ,query , *parameters ):
        if len( self.attr) == 0 :
            return False

        #先查找数据,确认存在
        if self.find().where(query ,*parameters ).count() != 0:
            key = []
            args = []
            for k in self.attr.keys():
                key.append( '`' + k + '` = %s ' )
                args.append( self.attr[ k ] )

            for item in parameters:
                args.append( item )

            where = self.sqlStr( query )

            sql = 'UPDATE `'+ self.db_name +'` SET '+ ','.join( key ) +' WHERE ' + where + ' LIMIT 1'

            return self.db.execute( sql , *args)
        return False