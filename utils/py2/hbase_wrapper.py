# # coding: utf-8 
import urllib2
import urllib
import json, time, requests, datetime
from logger_helper import logger 

class HbaseConsumer(object):
    def __init__(self, arg):
        self.msg = arg
        self.cert_id = (arg.get("cert_id")).encode('utf-8')
        self.api_key = arg.get("api_key")

    def curl_hbase(self):   
        feat_info = ''
        logger.info("api_key, cert_id:%s api_key:%s" %(self.cert_id, self.api_key))
        if self.api_key == 'userinfo':
            feat_info = self.curl_userinfo(self.cert_id)
        elif self.api_key == 'devinfo': 
            feat_info = self.curl_devinfo(self.cert_id)
        return feat_info        

     # get userinfo_feature
    def curl_userinfo(self, cert_id):    
        cur_url = "http://100.114.241.34:8764/data_service_query_route/query_rule/HBASE_E_001?"   

        params = {
            "cardId":cert_id,
            "code" : "T_WK_SE0002"
                }
        #post wk_wk_customer
        json_param = {"jsonParam" : params}
        post_data1 = urllib.urlencode(json_param)
        response1 = urllib2.urlopen(cur_url, post_data1)
        msg1 = json.loads(response1.read())
        data = {}
        if msg1.get("data") is not None:
            data["sex"] = msg1.get("data")[0].get("SEX")             
            data["age"] = None
            birth_day = msg1.get("data")[0].get("BIRTHDAY")
            if birth_day is not None or birth_day != '':
                days = (datetime.datetime.now() - datetime.datetime.strptime(birth_day, "%Y-%m-%d")).days
                age = days / 365
                data["age"] = age
        else:
            return False   

        #post wk_wk_customer_extend 
        params["code"] = "T_WK_SE0003"
        post_data2 = urllib.urlencode({"jsonParam": params})
        response2 = urllib2.urlopen(cur_url, post_data2)
        msg2 = json.loads(response2.read())
        if msg2.get("data") is not None:
            data["industry"] = msg2.get("data")[0].get("industry")
            data["marriage"] = msg2.get("data")[0].get("marriage")
            data["education"] = msg2.get("data")[0].get("education")
            return data 
        else:
            return False

     #get userinfo_feature 
    def curl_devinfo(self, certId):
        cur_url = "http://100.114.241.34:8764/data_service_query_route/query_rule/HBASE_E_001?"  
        
        params = {"cardId" : certId, "code" : "T_WK_SE0001"}
        post_data = urllib.urlencode({"jsonParam": params})
        response = urllib2.urlopen(cur_url, post_data)

        msg = json.loads(response.read())
        if msg.get("data") is not None:
            device_type = msg.get("data")[0].get("devicetype")
            data = {}
            data['device_type'] = device_type
            return data 
        else:
            return False

class HbaseWriter(object):
    
    def set_hbase(self, arg, url):
        data = {
            "appName":"ai_test",
            "name":"zzd",
            "phone":"1234556",
            "auth":{"code":"8899"}
            }
        data["param"] = arg
        post_data = json.dumps(data)
        response = requests.post(url + post_data)
        logger.info("write hbase %s" %(str(response.content)))
        return response.content
