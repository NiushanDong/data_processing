# coding: utf-8
import sys,os,traceback
import ssl
import json
from kafka import KafkaConsumer, KafkaProducer
from kafka.errors import KafkaError
from ConfigParser import SafeConfigParser

#milli seconds
reconnect_backoff_ms_value = 200
reconnect_backoff_max_ms_value = 120*1000

#config
config = SafeConfigParser()                                                                                                                  
path = "../../config/db.conf"
config.read(path)
username = config.get("aliyun", "sasl_plain_username")
password = config.get("aliyun", "sasl_plain_password")

#context 
context_path = "../../config/ca-cert"
context = ssl.create_default_context()
context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
context.verify_mode = ssl.CERT_REQUIRED
context.load_verify_locations(context_path)

#seconds
flush_time_out_value = 3

class Ali_Kafka_producer():
    def __init__(self, kafka_host,kafka_topic):
        self.kafka_host = kafka_host
        self.kafka_topic = kafka_topic
        self.producer = KafkaProducer(
                bootstrap_servers=kafka_host,
                sasl_mechanism="PLAIN",
                ssl_context=context,
                security_protocol='SASL_SSL',
                api_version = (0,10),
                retries=5,
                sasl_plain_username=username,
                sasl_plain_password=password,
                reconnect_backoff_ms=reconnect_backoff_ms_value)
    
    def send_data(self, params, key = None):
        try:
            params_msg = json.dumps(params)
            self.producer.send(self.kafka_topic,params_msg.encode('utf-8'), key)
            #self.producer.flush(flush_time_out_value)
        except KafkaError as e:
            print("Kafka producer error %s" %(e))
            return False
        else:
            return True

#Note however that there cannot be more consumer instances in a consumer group than partitions.
class Ali_Kafka_consumer():
    def __init__(self, kafka_host, kafka_topic, group_id):
        self.kafka_host = kafka_host
        self.kafka_topic = kafka_topic
        self.group_id = group_id
		
        self.consumer = KafkaConsumer(
                enable_auto_commit = False,
                group_id = self.group_id,
                sasl_mechanism="PLAIN",
                ssl_context=context,
                security_protocol='SASL_SSL',
                api_version = (0,10),
                sasl_plain_username=username,
                sasl_plain_password=password,
                fetch_max_bytes = 104785600,
                max_partition_fetch_bytes = 104785600,
                reconnect_backoff_ms = reconnect_backoff_ms_value,
                reconnect_backoff_max_ms = reconnect_backoff_max_ms_value,
                bootstrap_servers = self.kafka_host)
        
        self.consumer.subscribe(self.kafka_topic)

    def consume_data(self):
        try:
            for message in self.consumer:
                data = message.value 
                print(message.offset)
                print("RCV:" + data)
                self.consumer.commit()
        except KafkaError as e :
            print("Kafka consumer error %s" %(e))

