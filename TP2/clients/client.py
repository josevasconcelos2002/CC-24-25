import json
import socket
import struct
import uuid
from tasks.parser import parseTasks
from tasks.task import Task
from misc.sendMessage import sendMessage
import threading
import time
import random

class Client: 

    def __init__(self, server_ip: str, server_port: int, client_id: str = None):
        # Se o client_id não for fornecido, gera um ID aleatório
        self.id = client_id if client_id else str(uuid.uuid4())
        self.server_ip = server_ip
        self.server_port = server_port
        self.UDP_socket = self.setup_UDP_socket()
        self.TCP_socket = None  # socket TCP só é criado quando necessário
        self.Tasks = []
        self.connected = False
        self.lock = threading.Lock()
        self._stop_event = threading.Event()
        self.sequences = {}
        self.sequence = 0





    def setup_UDP_socket(self):
        # Create a UDP socket
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_socket.bind(('127.0.0.'+ str(random.randint(2, 100)), random.randint(1, 65535)))
        return udp_socket
    

    def send_initial_info(self):
        while self.connected == False and not self._stop_event.is_set():

        
            # Send this message to the server over UDP
            self.UDP_socket.settimeout(5)
            try:
                sendMessage(self.UDP_socket, (self.server_ip, self.server_port), self.id, 0)
                print(f"Sent initial client info to server: {self.id}")
            except socket.timeout:
                print(f"Timeout occured!")
            finally:
                self.UDP_socket.settimeout(None)
                break



    def listen_for_datagrams(self):
        buffer_size = 1024
        while not self._stop_event.is_set():
            try:
                print(f"Client listening:\n")
                data, addr = self.UDP_socket.recvfrom(buffer_size)
                if data:
                    self.handle_datagram(data, addr)
            except ConnectionResetError as e:
                print(f"Connection reset error: {e}")
                break
            except OSError as e:
                print(f"OS error (likely socket issue): {e}")
                break



    def parseTask(self, sequenceLength):
        taskList = [self.sequences[i] for i in range(sequenceLength)]
        return "".join(taskList)





    
    def handle_datagram(self,data, addr):
        # Decodifique os dados recebidos de bytes para string
        print(f"Received raw data: {data}")
        payload = data[14:]
        payload = payload.decode('utf-8')  # 'ignore' skips invalid bytes
        headers = data[:10]
        sequence = data[10:14]
        source_port, dest_port, length, checksum, messageType = struct.unpack('!HHHHH', headers)
        sequence_number, sequence_length = struct.unpack('!HH', sequence)
        print(f"Received data: {payload}\n")
        print(f"Adrr: {addr}\n")
        
        # Verifique se a mensagem contém um ID para processar os dados do cliente
        if messageType == 0:


            # Obtenha os dados do cliente e valide se todos os campos estão presentes
            with self.lock:        
                self.server_port = int(payload)
                #print(str(self.server_port)+" here")
                self.connected = True

        else:
            if messageType == 1:
            #with self.lock:
                time.sleep(3)
                sendMessage(self.UDP_socket, (self.server_ip, self.server_port), "Received", 1)
                self.sequences[sequence_number] = payload
                self.sequence += 1
                print("\nSequence: " + str(self.sequence))
                print("Sequence Length: " + str(sequence_length))
                if self.sequence == sequence_length:
                    # parseTask
                    taskString = self.parseTask(sequence_length)
                    print(taskString)
                    
                    
                    # Converte a string JSON para um dicionário Python
                    taskDict = json.loads(taskString)
                        
                    # parse taskString to Task
                    taskId = taskDict["task_id"]
                        
                    # Chama a função `parseTasks` com o `taskId` e o `taskDict`
                    taskObject = parseTasks(taskId, taskDict)
                        
                    # guardar Task no self.Tasks atraves do metodo append
                    self.Tasks.append(taskObject)
                    for task in self.Tasks:
                        print(task.to_dict())
                    # Enviar Ack para o servidor

                    # Criar Threads no cliente : Metrics Thread, AlertFlow Thread , Execute Task Thread

                    # Execute Task

                    #print(self.server_port)


    def to_dict(self):
        # Retorna os dados do cliente como um dicionário
        return {
            "id": self.id,
            "server_ip": self.server_ip,
            "server_port": self.server_port,
            "Tasks": self.Tasks
        }

    def close(self):
        with self.lock:
            self.UDP_socket.close()
            self._stop_event.set()
            # Close the socket
