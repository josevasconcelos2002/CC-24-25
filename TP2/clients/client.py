import json
import socket
import struct
import uuid
from tasks.config import AlterflowConditions
from tasks.parser import parseTasks
from tasks.task import Task
from misc.sendMessage import sendMessage
import threading
import time
import random
import subprocess
import psutil
import shlex
import os
from datetime import datetime

class Client: 

    def __init__(self, server_ip: str, server_port: int, client_id: str = None):
        # Se o client_id não for fornecido, gera um ID aleatório
        self.id = client_id if client_id else str(uuid.uuid4())
        self.server_ip = server_ip
        self.server_port = server_port
        self.UDP_socket = self.setup_UDP_socket()
        self.TCP_socket = self.setup_TCP_socket()  # socket TCP só é criado quando necessário
        self.Tasks = []
        self.connected = False
        self.lock = threading.Lock()
        self._stop_event = threading.Event()
        self.sequences = {}
        self.sequence = 0
        self.doingTask = False





    def setup_UDP_socket(self):
        # Create a UDP socket
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_socket.bind(('0.0.0.0', random.randint(1, 65535)))
        return udp_socket

    def setup_TCP_socket(self):
        # Create a UDP socket
        tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_socket.bind(('0.0.0.0', random.randint(1, 65535)))
        return tcp_socket
    

    def send_initial_info(self):
        while self.connected == False and not self._stop_event.is_set():
            # Send this message to the server over UDP
                sendMessage(self.UDP_socket, (self.server_ip, self.server_port), self.id, 0)
                print(f"Sent initial client info to server: {self.id}")
                time.sleep(5)
           


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

    def executeTask(self, command:str):
        with self.lock:
            self.doingTask = True
        try:
            # Split the command safely
            args = shlex.split(command)
        
        # Execute the command and capture output
            response = subprocess.run(args, capture_output=True, text=True)
        
        # Check for errors
            if response.returncode != 0:
                output = f"Error: {response.stderr}"
            else:
                output = response.stdout
        
        # Send the response via UDP
            time.sleep(5)
            output = response.stdout
            with self.lock:
                self.doingTask = False
                
                self.TCP_socket.close()
                print ("TCP SOCKET FECHADA")
                
            sendMessage(self.UDP_socket, (self.server_ip, self.server_port), output, 2)
    
    
        except Exception as e:
        # Handle unexpected exceptions
            error_message = f"An error occurred: {str(e)}"
            sendMessage(self.UDP_socket, (self.server_ip, self.server_port), error_message, 2)


    
    def alert_conditions(self,alertFlowConditions: AlterflowConditions,cpu_percentage_usage: float, ram_percentage_usage: float):
        send_alert = False
        if(alertFlowConditions.cpu_usage <= cpu_percentage_usage or alertFlowConditions.ram_usage <= ram_percentage_usage):
            send_alert = True
        return send_alert

    def medir(self, task: Task):
        task_id = task.task_id
        frequency = task.frequency
        duration = task.duration
        cpu = 0
        ram = 0
        """
        if task.config.device_metrics.cpu_usage == True:
            cpu = psutil.cpu_percent(interval=0)
        if task.config.device_metrics.ram_usage == True:
            ram = psutil.virtual_memory().percent
        """
        for i in range(0,int(duration/frequency)):
            if task.config.device_metrics.cpu_usage == True:
             cpu = psutil.cpu_percent(interval=0)
            if task.config.device_metrics.ram_usage == True:
             ram = psutil.virtual_memory().percent
            for j in range(1,frequency):
                if cpu != 0:
                    cpu = cpu + psutil.cpu_percent(interval=0)
                if ram != 0:
                    ram = ram + psutil.virtual_memory().percent
                time.sleep(1)
            if cpu != 0 and ram != 0:
                
                sendMessage(self.UDP_socket, (self.server_ip,self.server_port), "cpu_usage: " + str(cpu/(frequency+1)) + "'%' ram_usage: " + str(ram/(frequency+1)) + '%', 3)
            else: 
                if cpu != 0:
                   
                    sendMessage(self.UDP_socket, (self.server_ip,self.server_port), "cpu_usage: " + str(cpu/(frequency+1)) + '%', 3)
                else: 
                    if ram != 0:
                        
                        sendMessage(self.UDP_socket, (self.server_ip,self.server_port), "ram_usage: " + str(ram/(frequency+1))+ '%', 3)
        
        if task.config.alterflow_conditions.alterflow_conditions == True :
            print("\nDO WE NEED TO ALERT SERVER ?\n")
            print(f"\nCPU usage % : {cpu/(frequency+1)}\n")
            print(f"CPU alertFlow conditions % : {task.config.alterflow_conditions.cpu_usage}\n")
            print(f"\nRAM usage % : {ram/(frequency+1)}\n")
            print(f"RAM alertFlow conditions % : {task.config.alterflow_conditions.ram_usage}\n")
        
            send_alert_notification = self.alert_conditions(task.config.alterflow_conditions,cpu/(frequency+1), ram/(frequency+1))
            if(send_alert_notification):
                #send  a alert TCP datagram 
                print("\nALERT! CLIENT MUST SEND A ALERT TO THE SERVER\n")

    """      
    def alterFlow(self, task):
        message =  struct.pack('!H', 1) + (task.task_id + " " + self.id).encode('utf-8') 
        self.TCP_socket.send(message)
        time.sleep(3)
        while True: #self.doingTask == True:
            cpu = psutil.cpu_percent(interval=0)  
            ram = psutil.virtual_memory().percent          
            send_alert_notification = self.alert_conditions(task.config.alterflow_conditions,cpu, ram)
            if(send_alert_notification):
                time = datetime.now()
                message =  struct.pack('!H', 2) + (time + '\n' + cpu + '\n' + ram + '\n').encode('utf-8')
                self.TCP_socket.send(message)
        self.TCP_socket.close()
    """
    
    def alterFlow(self, task):
     message = struct.pack('!H', 1) + task.task_id.encode('utf-8') + " ".encode('utf-8') + self.id.encode('utf-8') + b'\n'
     self.TCP_socket.sendall(message)
    
     while self.doingTask:
         cpu = psutil.cpu_percent(interval=1)  
         ram = psutil.virtual_memory().percent          
         send_alert_notification = self.alert_conditions(task.config.alterflow_conditions, cpu, ram)
        
         if send_alert_notification:
             current_time = str(datetime.now())
             try:
                 message = struct.pack('!H', 2) + current_time.encode('utf-8') + b'\n' + str(cpu).encode('utf-8') + b'\n' + str(ram).encode('utf-8')+ b'\n'
                 
                 self.TCP_socket.sendall(message)
                 
             except socket.error as e:
                 print(f"Socket send error: {e}")
                 break  # stop further attempts on errors
         time.sleep(1)  # avoid maxing out resource poll
     self.TCP_socket.close()
    

                



    def parseTask(self, sequenceLength):
        taskList = ""
        for i in range(sequenceLength):
            taskList = taskList + self.sequences[i] 
        # Converte a string JSON para um dicionário Python
        taskDict = json.loads(taskList)
                        
        # parse taskString to Task
        taskId = taskDict["task_id"]

                        
        # Chama a função `parseTasks` com o `taskId` e o `taskDict`
        taskObject = parseTasks(taskId[2:], taskDict)  

        print(taskObject.to_bytes())
        if taskObject.config.alterflow_conditions.alterflow_conditions == True:
            self.TCP_socket.connect((self.server_ip, 54322))
        exec_thread = threading.Thread(target=self.executeTask, args=(taskObject.type,))
        exec_thread.daemon = True
        exec_thread.start()
        if taskObject.config.alterflow_conditions.alterflow_conditions == True:
            alter_thread = threading.Thread(target=self.alterFlow, args=(taskObject,))
            alter_thread.daemon = True
            alter_thread.start()   
        self.medir(taskObject)
        """
        medir_thread = threading.Thread(target=self.medir, args=(taskObject,))
        medir_thread.daemon = True
        medir_thread.start()
        """

        #return "".join(taskList)



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
                self.sequences[sequence_number] = payload
                self.sequence += 1
                print("\nSequence: " + str(self.sequence))
                print("Sequence Length: " + str(sequence_length))
                if self.sequence == sequence_length:
                    # parseTask
                    self.parseTask(sequence_length)
                    #print(taskString)
                    
                    self.sequence = 0
                    self.sequences = {}
                    # Enviar Ack para o servidor
                    sendMessage(self.UDP_socket, (self.server_ip, self.server_port),"Received", 0)

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