import json
import socket
import struct
import threading
from tasks.parser import parseTasks
from tasks.config import Config, Device_metrics, AlterflowConditions, LatencyConfig, Link_metrics
from tasks.task import Task
from tasks.tasks import Tasks
from clients.clients import Clients
from clients.client_server import ClientServer
from server.NMS_server_UDP import NMS_server_UDP
import random
import time

class NMS_server:

    def __init__(self):
        self.lastTask = 1
        self.tasks = Tasks()
        self.waitingTasks = {}
        self.currentTask = 1
        self.clients = Clients()
        self.UDP_socket = self.setup_UDP_socket(('127.0.0.1', 54321))  # Initialize the UDP socket
        self.TCP_socket = self.setup_TCP_socket()  # Initialize the TCP socket
        self.threads = []
        self.cond = threading.Condition()
        self.lock = threading.Lock()
        self._stop_event = threading.Event()

        # Inicia uma thread para escutar clientes UDP
        #udp_thread = threading.Thread(target=self.listen_for_datagrams, args=(self.UDP_socket,))
        #udp_thread.start()
        #self.threads.append(udp_thread)

    def setup_UDP_socket(self, addr):
        # Creates a UDP socket
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_socket.bind(addr)  # Bind to localhost and a specified port
        return udp_socket
    
    def setup_TCP_socket(self):
        # Creates a TCP socket
        TCP_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        TCP_socket.bind(('127.0.0.1', 54322))
        return TCP_socket

    def sendMessage(self, socket, addr, data):
        # Build the UDP datagram with the defined structure
        source_port = socket.getsockname()[1]  # Source port (can be configurable)
        dest_port = addr[1]

        data = data.encode('utf-8')

        chunk_size = 400
        chunks = [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]

        sequence_number = 0
        sequence_length = len(chunks)

        for info in chunks:

            # UDP header fields
            length = 13 + len(info)  # UDP header (8 bytes) + data
            checksum = 0  # Simulated, checksum calculation not implemented

            # Pack the UDP header fields
            udp_header = struct.pack('!HHHH', source_port, dest_port, length, checksum)
            # Pack additional protocol fields
            message = struct.pack('!II', sequence_number, sequence_length) + info

            sequence_number += 1
        
            # Combine the UDP header with the message
            datagram = udp_header + message

            print(f"datagram: {datagram}\n")
        
            # Send the datagram to the server
            self.UDP_socket.sendto(datagram, addr)
            #print(f"Datagram sent: Seq: {sequence_number}, Type: {message_type}, Data: {data.decode('utf-8')}")

    def parse_json(self, path: str):
        # Existing code for parsing JSON remains unchanged
        with open(path, "r") as file:
            tasks_json = json.load(file)

        if not tasks_json:
            print("error")
        else:
            print(f"success {len(tasks_json)}")

        for task in tasks_json:
            task_obj = parseTasks(self.lastTask, task)
            self.lastTask += 1
            self.tasks.add_task(task_obj)

        id = 1
        while True:
            t = self.tasks.get_task( str(id))
            if not t:
                break  # Exit loop if task is not found
            print(f"{t.task_id}  {t.type} {t.devices}")
            id += 1




    def processTask(self):
        while not self._stop_event.is_set() and self.currentTask <= len(self.tasks):
            task = self.tasks.get_task(self.currentTask)
            devices = task.getDevices()
            maxT = 3
            task_Threads = []
            nms_udp = NMS_server_UDP()

            for d in devices:
                client = self.clients.get_client(d)
                if not client:
                    time.sleep(1)
                    client = self.clients.get_client(d)

                if client:    
                    
                    with self.cond:
                        thread = threading.Thread(target=nms_udp.listen_for_datagrams, name =f"Thread-{d}", args=(self.cond,d, client.socket,))
                        nms_udp.threads[d] = thread
                        thread.start()
                    self.sendMessage(self.UDP_socket, client.address, task.to_bytes())    

                else:
                    self.waitingTasks[d] = task

            while nms_udp.threads:
                time.sleep(0.1)

            self.currentTask+=1




    def createPort(self):
        port = random.randint(1, 65535)
        clients = self.clients.to_dict()  # Corrected to call to_dict()

        # Iterate over client objects
        for id, client in clients.items():  # `client` should be a `ClientServer` instance
            # Ensure `client` has a valid socket and that it’s a socket object
            if hasattr(client, 'socket') and hasattr(client.socket, 'getsockname'):
                if client.socket.getsockname()[1] == port:
                    port = random.randint(1, 65535)

        return port



    def listen_for_datagrams(self, socket):
        buffer_size = 1024
        while not self._stop_event.is_set():
            try:
                print(f"Server listening:\n")
                data, addr = socket.recvfrom(buffer_size)
                if data:
                    self.handle_datagram(data, addr)
            except ConnectionResetError as e:
                print(f"Connection reset error: {e}")
                break
            except OSError as e:
                print(f"OS error (likely socket issue): {e}")
                break

    def handle_datagram(self,data, addr):
        # Decodifique os dados recebidos de bytes para string
        print(f"Received raw data: {data}")
        payload = data[16:]
        payload = payload.decode('utf-8')  # 'ignore' skips invalid bytes
        headers = data[:len(payload)]
        print(f"Received data: {payload}\n")
        print(f"Adrr: {addr}\n")
        
        # Verifique se a mensagem contém um ID para processar os dados do cliente
        if payload.startswith("ID:"):
            client_info = payload.split(",")
            client_data = {}
            
            # Extraia pares chave:valor do payload
            for info in client_info:
                if ":" in info:
                    key, value = info.split(":", 1)  # Limite de divisão para capturar valores completos
                    client_data[key.strip()] = value.strip()


            # Obtenha os dados do cliente e valide se todos os campos estão presentes
            client_id = client_data.get("ID")
            client_addr = addr

            port = self.createPort()

            socket = self.setup_UDP_socket(('127.0.0.1', port))

            self.sendMessage(socket, client_addr,"Ack," + "Port:"+str(port))



            if client_id and client_addr:
                with self.lock:
                    # Converta a porta para inteiro e adicione o cliente
                    #client = Client(client_id, server_ip, int(server_port))
                
                    client = ClientServer(addr, socket)
                    self.clients.add_client(client_id, client)
                    print(f"Client {client_id} added with Address {client_addr}")
                    print(f"{str(self.clients.to_dict())}\n")

                    if len(self.clients) == 1:
                        task_thread = threading.Thread(target=self.processTask)
                        task_thread.start()
                        self.threads.append(task_thread)
                
            else:
                print("Erro: Dados do cliente ausentes ou incompletos na mensagem de registro.")
        else:
            # Processa outras mensagens
            print(f"Received non-registration data: {payload}")

    def close(self):
            self._stop_event.set()
            self.threads[0].join()
            # Close the socket
            self.UDP_socket.close()
            self.TCP_socket.close()
