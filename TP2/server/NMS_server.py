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
from misc.sendMessage import sendMessage
from misc.openFile import openFile

import random
import time

class NMS_server:

    def __init__(self, storage_path):
        self.lastTask = 1
        self.tasks = Tasks()
        self.waitingTasks = {}
        self.currentTask = 1
        self.clients = Clients()
        self.UDP_socket = self.setup_UDP_socket(('', 54321))  # Initialize the UDP socket
        self.TCP_socket = self.setup_TCP_socket(('', 54322))  # Initialize the TCP socket
        self.threads = []
        self.cond = threading.Condition()
        self.lock = threading.Lock()
        self._stop_event = threading.Event()
        self.storage_path = storage_path

        # Inicia uma thread para escutar clientes UDP
        #udp_thread = threading.Thread(target=self.listen_for_datagrams, args=(self.UDP_socket,))
        #udp_thread.start()
        #self.threads.append(udp_thread)

    def setup_UDP_socket(self, addr):
        # Creates a UDP socket
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_socket.bind(addr)  # Bind to localhost and a specified port
        return udp_socket
    
    def setup_TCP_socket(self, addr):
        # Creates a TCP socket
        TCP_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        TCP_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        TCP_socket.bind(addr)
        return TCP_socket


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
            nms_udp = NMS_server_UDP(self.storage_path)

            if task.config.link_metrics.use_iperf == True:
                server = self.clients.get_client(task.config.link_metrics.server)
                if not server:
                   time.sleep(5)
                   server = self.clients.get_client(task.config.link_metrics.server)
                if server:
                    task.config.link_metrics.server_address = server.address
                    sendMessage(self.UDP_socket, server.address, str(task.config.link_metrics.duration), 4)
                else:
                    for d in devices:
                        self.waitingTasks[d] = task
                    break

            for d in devices:
                client = self.clients.get_client(d)
                if not client:
                    time.sleep(1)
                    client = self.clients.get_client(d)

                if client:    
                    
                    with self.cond:
                        thread = threading.Thread(target=nms_udp.listen_for_datagrams, name =f"Thread-{d}", args=(self.cond,d, client.socket, client.address, task,))
                        nms_udp.threads[d] = thread
                        thread.daemon = True
                        thread.start()
                    #self.sendMessage(self.UDP_socket, client.address, task.to_bytes())    

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
                print(f'Data received')
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
        payload = data[14:]
        payload = payload.decode('utf-8')  # 'ignore' skips invalid bytes
        headers = data[:10]
        sequence = data[10:14]
        source_port, dest_port, length, checksum, messageType = struct.unpack('!HHHHH', headers)
        sequence_number, sequence_length = struct.unpack('!HH', sequence)
        print(f"Received data: {payload}\n")
        print(f"Adrr: {addr}\n")
        if messageType == 2:
            print(f"Received data: {payload}\n")

        
        # Verifique se a mensagem contém um ID para processar os dados do cliente
        if messageType == 0:

            # Obtenha os dados do cliente e valide se todos os campos estão presentes
            client_id = payload
            client_addr = addr

            port = self.createPort()

            socket = self.setup_UDP_socket(('0.0.0.0', port))

            sendMessage(socket, client_addr, str(port), 0)



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
                        task_thread.daemon = True
                        task_thread.start()
                        self.threads.append(task_thread)
                    else: 
                        print("Erro. Length not valid")
                
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

    def handle_client(self , conn, addr):
        """Function to handle communication with a single client."""
        print('Connected by', addr)
        file = None
        with conn:
            while True:
                data = conn.recv(1024)
                if not data:
                 break
                headers = data[:2]
                messageType = struct.unpack('!H',headers)

                decoded_data = data[2:].decode('utf-8')
                print(f'Aqui está a message tpye: {messageType}')

                if messageType[0] == 1:
                    print(f'Aqui está a decoded data: {decoded_data}')
                    info = decoded_data.split()
                    file = openFile(info[0], info[1], self.storage_path)
                else:
                    print(f'Aqui está a decoded data: {decoded_data}')
                    file.write(f"AlterFlow: {decoded_data}\n")
                    file.flush()

        print(f"Connection with {addr} closed.")

    def listen_TCP(self, socket):
        #s.listen()
        self.TCP_socket.listen()
        
        print(f"TCP a ouvir")
        while True:
            conn, addr = self.TCP_socket.accept()
            # Start a new thread to handle the client
            client_thread = threading.Thread(target=self.handle_client, args=(conn, addr))
            client_thread.daemon = True  # Ensures threads close when the main program exits
            client_thread.start()
