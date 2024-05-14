# -*- coding: utf-8 -*-
"""
Created on Tue Apr 30 17:37:32 2024

@author: Diao Group
"""

import pika
import random
import json
from datetime import datetime
from tools.ultimusExtruder import *
from axes.lulzbotTaz6_BP import *

class RpcDevicesAdaptor(object):

    def __init__(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='localhost', heartbeat=0))

        self.channel = self.connection.channel()

        self.channel.queue_declare(queue='rpc_queue')
        self.channel.exchange_declare(exchange='device_commands', exchange_type='direct')
        
        self.deviceIDs = {'ultimusExtruder': '0x0', 'lulzbot': '0x1'}
        extruder = ultimusExtruder()
        lulzbot = lulzbotTaz6_BP()
        self.devices = {
            'ultimusExtruder': {'instance': extruder, 'type': 'tool'}, 
            'lulzbot': {'instance': lulzbot, 'type': 'axes'},
            }
        
        # self.deviceIDs = {'device_0':'0x0', 'device_1':'0x1', 'device_2':'0x2', 'device_3':'0x3', 'device_4':'0x4', 
        #     'device_5':'0x5', 'device_6':'0x6', 'device_7':'0x7', 'device_8':'0x8', 'device_9':'0x9'}
        self.queue_names = []
        for deviceTitle, deviceID in self.deviceIDs.items():
            result = self.channel.queue_declare(queue='')
            queue_name = result.method.queue
            self.queue_names.append(queue_name)
            self.channel.queue_bind(
                exchange='device_commands', queue=queue_name, routing_key=deviceID)

    def get_channel(self):
        return self.channel
    
    def get_queue_names(self):
        return self.queue_names
    
    def generate_status(self, deviceTitle):
        device = self.devices[deviceTitle]
        isConnected = device['instance'].activate()
        return isConnected

    def generate_command_status(self):
        return random.choice(['Executing', 'Finished', 'Queued'])

    def getDevicesStatus(self):
        # {'_id': 0, 'title': 'device_0', 'isConnected': True}
        devicesStatusList = []
        
        for deviceTitle, deviceId in self.deviceIDs.items():
            status = self.generate_status(deviceTitle)
            devicesStatusList.append({'_id': deviceId, 'title': deviceTitle, 'isConnected': status})
        return devicesStatusList

    def on_request(self, ch, method, props, body):
        print(f" [.] incomming message: {body}")
        # response = fib(n)
        status = json.dumps(self.getDevicesStatus())

        ch.basic_publish(exchange='',
                        routing_key=props.reply_to,
                        properties=pika.BasicProperties(correlation_id = \
                                                            props.correlation_id),
                        body=status)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def on_command_request(self, ch, method, props, body):
        json_body = json.loads(body)
        print(f" [.] incomming command: {json_body}")
        # {'command_id': str(uuid.uuid4()), 'command': 'testCommand', 'device_id': 'id_1'}
        device_id = json_body['device_id']
        command_id = json_body['command_id']
        
        device_command = json_body['command']
        
        print(f" [.] Time: {datetime.now()}, Incomming command for device {device_id}: {device_command}")
        
        device_command_list = device_command.split('_')
        if device_command_list[0] == 'testCommand':
            # Do nothing
            print('testing add device command, do nothing')
        elif device_command_list[0] == 'moveTo':
            # command = moveTo_x_y_z
            x_coord = float(device_command_list[1])
            y_coord = float(device_command_list[2])
            z_coord = float(device_command_list[3])
            print(f"moving device to (x, y, z): ({x_coord}, {y_coord}, {z_coord})")
        else:
            print(f"we don't support this command yet, direct default case, command = {device_command}")
        
        command_status = self.generate_command_status()
        status = json.dumps({
            'command_id': command_id, 'command_status': command_status, 'device_id': device_id
        })
        
        ch.basic_publish(exchange='',
                        routing_key=props.reply_to,
                        properties=pika.BasicProperties(correlation_id = \
                                                            props.correlation_id),
                        body=status)
        ch.basic_ack(delivery_tag=method.delivery_tag)
        print('sent response to:', props.reply_to)

if __name__ == "__main__":
    rpc_device_adaptor = RpcDevicesAdaptor()
    print(rpc_device_adaptor.getDevicesStatus())
    
    rpc_device_adaptor_channel = rpc_device_adaptor.get_channel()
    rpc_device_adaptor_channel.basic_qos(prefetch_count=1)
    rpc_device_adaptor_channel.basic_consume(queue='rpc_queue', on_message_callback=rpc_device_adaptor.on_request)
    for queue_n in rpc_device_adaptor.get_queue_names():
        rpc_device_adaptor_channel.basic_consume(queue=queue_n, on_message_callback=rpc_device_adaptor.on_command_request)

    print(" [x] Awaiting RPC requests")
    rpc_device_adaptor_channel.start_consuming()
