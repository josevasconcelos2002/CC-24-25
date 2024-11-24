import json
import socket
import struct
import threading
from tasks.config import Config, Device_metrics, AlterflowConditions, LatencyConfig, Link_metrics
from tasks.task import Task
from tasks.tasks import Tasks
from clients.clients import Clients
from clients.client_server import ClientServer
from misc.sendMessage import sendMessage
import random
import time

class NMS_server_UDP:

    def __init__(self):
        self.maxT = 3
        self.currentT = 0
        self.threads = {}



    def listen_for_datagrams(self, cond, device, socket, addr, task):
        buffer_size = 1024
        if self.currentT == self.maxT:
            cond.wait()
        self.currentT += 1
        sequence = 0
        received = False
        socket.settimeout(30)
        sendMessage(socket, addr, task.to_bytes(), 1)
        while not received:
            try:
                print(f"Server client listening:\n")
                data, addr = socket.recvfrom(buffer_size)
                #time.sleep(0.5)
                #print("stopping")
                #received = True
                #self.currentT -= 1
                #del self.threads[device]
                #with cond:
                    #cond.notify()

                if data:
                    #self.handle_datagram(data, addr)
                    
                    
                    
                    print(f"Received data length: {len(data)}")
                    payload = data[14:]
                    headers = data[:10]
                    seq = data[10:14]
                    source_port, dest_port, length, checksum, messageType = struct.unpack('!HHHHH', headers)
                    sequence_number, sequence_length = struct.unpack('!HH', seq)
                    print(payload.decode('utf-8'))
                    if messageType == 3:
                        print(payload.decode('utf-8'))
                    if messageType == 2:
                        print(payload.decode('utf-8'))
                        sequence += 1
                    """    
                    else:
                        print(payload.decode('utf-8'))
                    """
                    if sequence == sequence_length: 
                        del self.threads[device]
                        self.currentT -=1
                        received = True
                        print(payload.decode('utf-8')+" hello")
                        with cond:
                            cond.notify()
                    
            except socket.timeout:
                print(f"Timeout occured in {addr}!")
                sequence = 0
                sendMessage(socket, addr, task.to_bytes(), 1)
            except ConnectionResetError as e:
                print(f"Connection reset error: {e}")
                break
            except OSError as e:
                print(f"OS error (likely socket issue): {e}")
                break
            #finally:
                #break