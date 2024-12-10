# -*- coding: utf-8 -*-
import pymongo
import sys

class Singleton(object):
    # 单例模式写法,参考：http://ghostfromheaven.iteye.com/blog/1562618
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            orig = super(Singleton, cls)
            cls._instance = orig.__new__(cls, *args, **kwargs)
        return cls._instance


class MongoConn(Singleton):    
    def __init__(self, args):
        try:
            self.conn = pymongo.MongoClient( args["db_addr"], replicaSet= args["replicaSet"])
            self.username = args["user"]
            self.password = args["pw"] 
            if self.username and self.password:
                self.connected = self.conn.admin.authenticate(self.username, self.password)
            else:
                self.connected = True
            self.db = self.conn[args["db_name"]]
        except Exception:
             print 'Connect Statics Database Fail.'
    
    def insert(self, table, value):
        # 可以使用insert直接一次性向mongoDB插入整个列表，也可以插入单条记录，但是'_id'重复会报错
        try:
            self.db[table].insert(value, continue_on_error=True)
        except Exception as e:
            print str(e)

    def update(self, table, conditions, value):
        try:
            self.db[table].update(conditions, value)
        except Exception as e:
            print str(e)
    
    def upsert_one(self, table, data):
        try:
            query = {'_id': data.get('_id','')}
            if not self.db[table].find_one(query):
                self.db[table].insert(data)
            else:
                data.pop('_id')
                self.db[table].update(query, {"$set":data})
        except Exception as e:
            print str(e)
 	
    def find(self, table, data):
        try:
            query = {'_id':data}
            return self.db[table].find_one(query)
        except Exception as e:
            print str(e)   
