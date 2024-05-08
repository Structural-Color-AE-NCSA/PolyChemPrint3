# -*- coding: utf-8 -*-
"""
Created on Tue Apr 30 17:37:32 2024

@author: Diao Group
"""

import pika
import random
import json
from datetime import datetime
from tools.OmnicureS2000Elite import *
from tools.ultimusExtruder import *
from axes.lulzbotTaz6_BP import *

class testDevice(object):

    def __init__(self):
        self.deviceIDs = {'ultimusExtruder': '0x0', 'lulzbot': '0x1'}
        extruder = ultimusExtruder()
        lulzbot = lulzbotTaz6_BP()
        omnicureS2000Elite = OmnicureS2000Elite()
        self.devices = {
            'omnicureS2000Elite': {'instance': omnicureS2000Elite, 'type': 'tool'},
            'ultimusExtruder': {'instance': extruder, 'type': 'tool'},
            'lulzbot': {'instance': lulzbot, 'type': 'axes'},
            }
    
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
    
#     def send_command(self, command, device):
#         device = self.devices[deviceTitle]
#         if device['type'] == 'axes':
#             if len(command) > 11 and command[:11] == 'setPosMode_':
#                 device['instance'].setPosMode(command[11:])
#             elif len(command) > 5 and command[:5] == 'move_':
#                 device['instance'].move(command[5:])
#             else:
#                 print('command not recognized')
#                 return False
#         elif device['type'] == 'tool':
#             if len(command) >= 9 and command[:9] == 'setValue_':
#                 setValue_res = device['instance'].setValue(command[9:])
#                 if setValue_res[0] == -1:
#                     return False
#             elif command == 'on':
#                 engage_res = device['instance'].engage()
#                 if engage_res[0] == -1:
#                     return False
#             elif command == 'off':
#                 disengage_res = device['instance'].disengage()
#                 if disengage_res[0] == -1:
#                     return False
#             else:
#                 print('command not recognized')
#                 return False
#         return True
        
        
if __name__ == "__main__":
    testDevice = testDevice()
    print(testDevice.getDevicesStatus())
