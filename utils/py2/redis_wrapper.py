 # coding: utf-8 
import redis, time
from coordination import run_with_lock 
from logger_helper import logger
from ConfigParser import SafeConfigParser

config = SafeConfigParser()
path = "../../config/db.conf"                                                                                                                
config.read(path)
redis_pwd = config.get("redis", "redis_pwd")

class RedisCache(object):
    def __init__(self, host, port, db_ids, zk_url):
        self._host = host
        self._port = port
        self._connections =[]
        self._db_ids = db_ids
        self._zk_url = zk_url
    	
        if not hasattr(RedisCache, 'pool'):
    	    RedisCache.create_pool(self._db_ids, self._host, self._port)
        
        for i in self._db_ids:
            self._connections.append(redis.StrictRedis(
                connection_pool = RedisCache.pool[i]))
    
    @staticmethod
    def create_pool(db_ids, host, port):
        RedisCache.pool = []
        for i in db_ids:
            RedisCache.pool.append(
                redis.ConnectionPool(host = host, port = port, db = i,password=redis_pwd))

    def hset(self, name, key, value, db_id, ex=None, retry_num = 5):
        try: 
    	    self._connections[db_id].hset(name, key, value)
            if ex:
                return self._connections[db_id].expire(name,ex)
            else:
                return 
        except Exception as e:
            if retry_num > 0:
                time.sleep(5)
                return self.hset(name,key,value,db_id,ex,retry_num-1)
            else:
                logger.error("redis error %s" %(str(e)))
                return None
                #todo

    def hset_with_lock(self, lock_id, name, key, value, db_id, ex=None):
        return run_with_lock(self._zk_url, lock_id, self.hset, name, key, value, db_id, ex)

    def hsets(self, name, maps, db_id, ex=None, retry_num = 5):
        try:
            self._connections[db_id].hmset(name, maps)
            if ex:
                return self._connections[db_id].expire(name,ex)
            else:
                return
        except Exception as e:
            if retry_num > 0:
                time.sleep(5)
                return self.hsets(name,maps,db_id,ex,retry_num -1)
            else:
                logger.error("redis error %s" %(str(e)))
                return None


    def hsets_with_lock(self, lock_id, name, maps, db_id, ex=None):
        return run_with_lock(self._zk_url, lock_id, self.hsets, name, maps, db_id, ex)

    def hget(self, name, key, db_id, retry_num = 5):
        try:
    	    return self._connections[db_id].hget(name, key)
        except Exception as e:
            if retry_num > 0:
                time.sleep(5)
                return self.hget(name, key, db_id, retry_num -1)
            else:
                logger.error("redis error %s" %(str(e)))
                return None
    
    def hget_with_lock(self, lock_id, name, key, db_id):
        return run_with_lock(self._zk_url, lock_id, self.hget, name, key, db_id)

    def hgetall(self, name, db_id, retry_num = 5):
        try:
            return self._connections[db_id].hgetall(name)
        except Exception as e:
            if retry_num > 0:
                time.sleep(5)
                return self.hgetall(name,db_id, retry_num -1)
            else:
                logger.error("redis error %s" %(str(e)))
                return None
    
    def hgetall_with_lock(self, lock_id, name, db_id):
        return run_with_lock(self._zk_url, lock_id, self.hgetall, name, db_id)

    def set_data(self, key, value, db_id, ex=None, retry_num = 5):
        try:
            self._connections[db_id].set(key, value)
            if ex:
                return self._connections[db_id].expire(name,ex)
            else:
                return None
        except Exception as e:
            if retry_num > 0:
                time.sleep(5)
                return self.set_data(key, value, db_id, ex, retry_num -1)
            else:
                logger.error("redis error %s" %(str(e)))
                return None

    def set_data_with_lock(self, lock_id, key, value, db_id, ex=None):
        return run_with_lock(self._zk_url, lock_id, self.set_data, key, value, db_id, ex)

    def get_data(self, key, db_id, retry_num = 5):
        try:
            return self._connections[db_id].get(key)
        except Exception as e:
            if retry_num >0:
                time.sleep(5)
                return self.get_data(key,db_id, retry_num -1)
            else:
                logger.error("redis error %s" %(str(e)))
                return None

    def get_data_with_lock(self, lock_id, key, db_id):
        return run_with_lock(self._zk_url, lock_id, self.get_data, key, db_id)

    def del_data(self, key, db_id, retry_num =5):
        try:
            return self._connections[db_id].delete(key)
        except Exception as e:
            if retry_num > 0:
                time.sleep(5)
                return self.del_data(key, db_id, retry_num -1)
            else:
                logger.error("redis error %s" %(str(e)))
                return None

    def del_data_with_lock(self, lock_id, key, db_id):
        return run_with_lock(self._zk_url, lock_id, self.del_data, key, db_id)
    
