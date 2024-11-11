import json
import socket
import struct
import threading
from tasks.config import Config, Device_metrics, AlterflowConditions, LatencyConfig, Link_metrics
from tasks.task import Task
from tasks.tasks import Tasks
from clients.clients import Clients
from clients.client_server import ClientServer
import random
import time

class NMS_server_UDP:

    def __init__(self):
        self.maxT = 3
        self.currentT = 0
        self.threads = {}



    def listen_for_datagrams(self, cond, device, socket):
        buffer_size = 1024
        if self.currentT == self.maxT:
            cond.wait()
        self.currentT += 1
        sequence = 0
        received = False
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
                    
                    self.currentT -=1
                    del self.threads[device]
                    print(f"Received data length: {len(data)}")
                    payload = data[16:]
                    headers = data[:8]
                    seq = data[8:16]
                    source_port, dest_port, length, checksum = struct.unpack('!HHHH', headers)
                    sequence_number, sequence_length = struct.unpack('!II', seq)
                    sequence += 1
                    if sequence == sequence_length:
                        received = True
                    print(payload.decode('utf-8')+" hello")
                    with cond:
                        cond.notify()
            except ConnectionResetError as e:
                print(f"Connection reset error: {e}")
                break
            except OSError as e:
                print(f"OS error (likely socket issue): {e}")
                break
