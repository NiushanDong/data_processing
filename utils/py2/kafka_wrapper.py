# coding: utf-8
import sys,os,traceback
#sys.path.append("../utils/python")
from kafka import KafkaProducer
from kafka import KafkaConsumer
from kafka.errors import KafkaError
import json

#milli seconds
reconnect_backoff_ms_value = 200
reconnect_backoff_max_ms_value = 120*1000

#seconds
flush_time_out_value = 3

class Kafka_producer():
    def __init__(self, kafka_host,kafka_topic):
        self.kafka_host = kafka_host
        self.kafka_topic = kafka_topic
        self.producer = KafkaProducer(
                bootstrap_servers = self.kafka_host,
                reconnect_backoff_ms = reconnect_backoff_ms_value)
    
    def send_data(self,params):
        try:
            params_msg = json.dumps(params)
            self.producer.send(self.kafka_topic,params_msg.encode('utf-8'))
            self.producer.flush(flush_time_out_value)
        except KafkaError as e:
            print("Kafka producer error %s" %(e))
            return False
        else:
            return True

#Note however that there cannot be more consumer instances in a consumer group than partitions.
class Kafka_consumer():
    def __init__(self, kafka_host, kafka_topic, group_id):
        self.kafka_host = kafka_host
        self.kafka_topic = kafka_topic
        self.group_id = group_id
		
        self.consumer = KafkaConsumer(
                self.kafka_topic,
                enable_auto_commit = True,
                group_id = self.group_id,
                fetch_max_bytes = 104785600,
                max_partition_fetch_bytes = 104785600,
                reconnect_backoff_ms = reconnect_backoff_ms_value,
                reconnect_backoff_max_ms = reconnect_backoff_max_ms_value,
                bootstrap_servers = self.kafka_host)
    
    def consume_data(self):
        try:
            for message in self.consumer:
                data = message.value 
                print(message.offset)
                print("RCV:" + data)
                self.consumer.commit()
        except KafkaError as e :
            print("Kafka consumer error %s" %(e))

