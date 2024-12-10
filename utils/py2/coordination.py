 # coding: utf-8 
import os
from kazoo.client import KazooClient
from logger_helper import logger


#TODO, reconnect, recover lost lock
def my_listener(state):
    if state == KazooState.LOST:
        # Register somewhere that the session was lost
        logger.info("Zookeeper connection lost")
    elif state == KazooState.SUSPENDED:
        # Handle being disconnected from Zookeeper
        logger.info("Zookeeper disconnected")
    else:
        # Handle being connected/reconnected to Zookeeper
        logger.info("Zookeeper connected/reconnected")

class Singleton(object):
    _instance = None
    def __new__(cls, *args, **kw):
        if not cls._instance:
            cls._instance = super(Singleton, cls).__new__(cls, *args, **kw)  
        return cls._instance  

class CoordinationConnection(Singleton):
    def __init__(self, zk_url):
        self.zk = KazooClient(hosts=zk_url)
        self.zk.start()
        self.zk.add_listener(my_listener)

    def get_connection(self):
        return self.zk

class CoordinationLock():
    def __init__(self, zk_url, lock_id, client_identifier):
        self.zk = CoordinationConnection(zk_url).get_connection()
        self.lock = self.zk.Lock(
                "/" + str(lock_id), 
                "identifier-" + str(client_identifier))
		
    def acquire(self):
        status = self.lock.acquire()
        return status

    def release(self):
        self.lock.release()

def run_with_lock(zk_url, lock_id, func, *args):
    client_identifier = os.getpid()
    instance = CoordinationLock(zk_url, lock_id, client_identifier)
    status = instance.acquire()
    logger.info("Got lock {}".format(lock_id))
    ret = None
    try:
        ret = func(*args)
    except Exception as err:
        logger.info(err)
    instance.release()
    logger.info("Lock {} released".format(lock_id))
    
    return ret
