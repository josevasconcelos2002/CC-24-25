import json
import socket
import struct
import uuid
from tasks.config import AlertflowConditions
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
import re

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

                print ("TCP SOCKET FECHADA")
                
            sendMessage(self.UDP_socket, (self.server_ip, self.server_port), output, 2)
            with self.lock:
                self.doingTask = False
    
    
        except Exception as e:
        # Handle unexpected exceptions
            error_message = f"An error occurred: {str(e)}"
            sendMessage(self.UDP_socket, (self.server_ip, self.server_port), error_message, 2)


    
    def alert_conditions(self,alertFlowConditions: AlertflowConditions,cpu_percentage_usage: float, ram_percentage_usage: float):
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
        message_parts = []

        for i in range(0,int(duration/frequency)):
            messages_parts = []
            if task.config.device_metrics.cpu_usage:
             cpu = psutil.cpu_percent(interval=0)
            if task.config.device_metrics.ram_usage:
             ram = psutil.virtual_memory().percent
            for j in range(1,frequency):
                if cpu != 0:
                    cpu = cpu + psutil.cpu_percent(interval=0)
                if ram != 0:
                    ram = ram + psutil.virtual_memory().percent
                time.sleep(1)

            if task.config.device_metrics.cpu_usage:
               message_parts.append(f"cpu_usage: {(cpu/(frequency+1))}%")
            if task.config.device_metrics.ram_usage:
               message_parts.append(f"ram_usage: {(ram/(frequency+1))}%")

            if task.config.link_metrics.bandwidth:
                server_addr = task.config.link_metrics.server_address
                result = subprocess.run(["iperf", "-c", server_addr, "-t", "1", "-f", "g"], capture_output=True, text=True)

                if result.returncode == 0:
                # Procure pela linha que contém as informações de largura de banda usando regex
                  print(result.stdout)#.decode('utf-8'))
                  match = re.search(r"(\d+\sGBytes)\s+(\d+.\d+\sGbits/sec)", result.stdout)
                  if match:
                     transfer = match.group(1)  # Ex: "798 MBytes"
                     bandwidth = match.group(2).split()  # Ex: "6.66 Mbits/sec"
                     
                     bandwidth_mbps = float(bandwidth[0]) * 1000
                     message_parts.append(f"bandwidth: {bandwidth_mbps}Mbps") 
                  else:
                     print("Não foi possível extrair a largura de banda.")
                else:
                   print(f"Error: {result.stderr}")
                        
             


            if task.config.link_metrics.latency.latency or task.config.link_metrics.jitter or task.config.link_metrics.packet_loss:
               result = subprocess.run(["ping", "10.0.0.20", "-c", "4"], capture_output=True, text=True)

               if result.returncode == 0:
                 # Procure pelas estatísticas de RTT (min, avg, max, mdev)
                 rtt_match = re.search(r"min/avg/max/mdev = (\d+.\d+)/(\d+.\d+)/(\d+.\d+)/(\d+.\d+)", result.stdout)

                 loss_match = re.search(r"(\d+)% packet loss", result.stdout)

                 if rtt_match and loss_match:
                  # Extraia os valores de RTT
                  min_rtt = float(rtt_match.group(1))
                  avg_rtt = float(rtt_match.group(2))
                  max_rtt = float(rtt_match.group(3))
                  mdev_rtt = float(rtt_match.group(4))

                  packet_loss = float(loss_match.group(1))
                  if task.config.link_metrics.latency.latency:
                        message_parts.append(f"Latency: {avg_rtt}ms")                      
                  if task.config.link_metrics.jitter: 
                        print(f"\nMAX_RTT: {max_rtt}\n")
                        print(f"\nMIN_RTT: {min_rtt}\n")
                        jitter = max_rtt - min_rtt  
                        message_parts.append(f"Jitter: {jitter} ms")
                  if task.config.link_metrics.packet_loss:   
                        message_parts.append(f"Packet_loss: {(packet_loss)}%")

                 else:
                    print("Failed to extract RTT values from ping output.")

                 

               else:
                    # If the ping command fails, print the error and return None
                    print(f"Error: {result.stderr}")


            if message_parts:
                message = " ".join(message_parts)
                sendMessage(self.UDP_socket, (self.server_ip, self.server_port), message, 3)

    
    
    def alertFlow(self, task):
        message = struct.pack('!H', 1) + task.task_id.encode('utf-8') + b" " + self.id.encode('utf-8') + b'\n'
        self.TCP_socket.sendall(message)

        while self.doingTask:
            cpu = psutil.cpu_percent(interval=1)  
            ram = psutil.virtual_memory().percent          
            send_alert_notification = self.alert_conditions(task.config.alertflow_conditions, cpu, ram)

            if send_alert_notification:
                current_time = str(datetime.now())
                try:
                    cpu_string = "cpu_usage -> " + str(cpu) + " %"
                    ram_string = "ram_usage -> " + str(ram) + " %"
                    message = struct.pack('!H', 2) + current_time.encode('utf-8') + b'\n' + cpu_string.encode('utf-8') + b'\n' + ram_string.encode('utf-8') + b'\n'
                    self.TCP_socket.sendall(message)
                except socket.error as e:
                    print(f"Socket send error: {e}")
                    break  # stop further attempts on errors
            time.sleep(1)  # Avoid overloading resource polling
        self.TCP_socket.close()
        self.TCP_socket = self.setup_TCP_socket()




    def parseTask(self, sequenceLength):
        taskList = ""
        for i in range(sequenceLength):
            taskList += self.sequences[i] 
        # Converte a string JSON para um dicionário Python
        taskDict = json.loads(taskList)

        # Parse taskString to Task
        taskId = taskDict["task_id"]
        taskObject = parseTasks(taskId[2:], taskDict)

        print(taskObject.to_bytes())
        if taskObject.config.alertflow_conditions.alertflow_conditions:
            self.TCP_socket.connect((self.server_ip, 54322))

        # Inicia as threads necessárias
        exec_thread = threading.Thread(target=self.executeTask, args=(taskObject.type,))
        exec_thread.daemon = True
        exec_thread.start()

        if taskObject.config.alertflow_conditions.alertflow_conditions:
            alert_thread = threading.Thread(target=self.alertFlow, args=(taskObject,))
            alert_thread.daemon = True
            alert_thread.start()

        self.medir(taskObject)

        """
        medir_thread = threading.Thread(target=self.medir, args=(taskObject,))
        medir_thread.daemon = True
        medir_thread.start()
        """

        #return "".join(taskList)

    def do_iperf(self, duration):
        command = ["iperf", "-s", "-t", duration]

        # Start the iperf3 server using subprocess.run
        try:
            # Running the iperf3 server in blocking mode (it will run until interrupted)
            subprocess.run(command, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error while running iperf3 server: {e}")




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
            else:
                if messageType == 4:
                    self.do_iperf(payload)


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