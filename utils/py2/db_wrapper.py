import MySQLdb
from MySQLdb.cursors import DictCursor
from DBUtils.PooledDB import PooledDB  
from logger_helper import logger

class Mysql(object): 
    __pool = None
    def __init__(self, ip, port, user, pwd, dtype, database):
        print ip,port,pwd
        self._conn = Mysql.__getConn(ip, port, user, pwd, dtype, database) 
        self._cursor = self._conn.cursor()

    @staticmethod
    def __getConn(ip, port, user, pwd, dtype, database):
        if Mysql.__pool is None:
            __pool = PooledDB(creator = MySQLdb, mincached=1,maxcached=20, 
                    host=ip, port=port,user=user,passwd=pwd,charset=dtype,
                    db = database ,cursorclass=DictCursor)
        return __pool.connection()

    def getOne(self, sql, param=None):
        # according to sql, get one result 
        if param is None: 
            count = self._cursor.execute(sql) 
        else:
            count = self._cursor.execute(sql, param) 
        
        if count>0: 
            result = self._cursor.fetchone() 
        else:
            result = False
        
        return result

    def getAll(self, sql, param=None):
        # according to sql, get all results
        if param is None:
            count = self._cursor.execute(sql)
        else:
            count = self._cursor.execute(sql, param)

        if count > 0:
            result = self._cursor.fetchall()
        else:
            result = False

        return result

    def getMany(self, sql, num, param=None):
        # according to sql, get nums results 
        if param is None:
            count = self._cursor.execute(sql)
        else:
            count = self._cursor.execute(sql, param)

        if count > 0:
            result = self._cursor.fetchmany(num)
        else:
            result = False

        return result

    def insertOne(self, sql, value):
        self._cursor.execute(sql, value)
        self._conn.commit()
        return self.__getInsertId()

    def insertMany(self, sql, values):
        count = self._cursor.executemany(sql,values)
        self._conn.commit()
        return count

    def __getInsertId(self):
        self._cursor.execute("SELECT @@IDENTITY AS id")
        result = self._cursor.fetchall()
        return result[0]['id']


    def __query(self, sql, param=None):
        if param is None:
            count = self._cursor.execute(sql)
        else:
            count = self._cursor.execute(sql, param)

        return count 

    def update(self, sql, param=None):
        return self.__query(sql, param)

    def delete(self, sql, param=None):
        return self.__query(sql, param)

    def begin(self):
        self._conn.autocommit(0)

    def end(self, option='commit'):
        if option == 'commit':
            self._conn.commit()
        else:
            self._conn.rollback()

    def dispose(self, isEnd=1):
        if isEnd == 1:
            self.end('commit')
        else:
            self.end('rollback')

        self._cursor.close()
        self._conn.close()


