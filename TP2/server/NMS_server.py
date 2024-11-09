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

class NMS_server:

    def __init__(self):
        self.lastTask = 1
        self.tasks = Tasks()
        self.currentTask = 0
        self.clients = Clients()
        self.UDP_socket = self.setup_UDP_socket(('127.0.0.1', 54321))  # Initialize the UDP socket
        self.TCP_socket = self.setup_TCP_socket()  # Initialize the TCP socket
        self.threads = []
        self._stop_event = threading.Event()

        # Inicia uma thread para escutar clientes UDP
        udp_thread = threading.Thread(target=self.listen_for_datagrams)
        udp_thread.start()
        self.threads.append(udp_thread)

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

        for info in chunks:

            # UDP header fields
            length = 13 + len(info)  # UDP header (8 bytes) + data
            checksum = 0  # Simulated, checksum calculation not implemented

            # Pack the UDP header fields
            udp_header = struct.pack('!HHHH', source_port, dest_port, length, checksum)
            # Pack additional protocol fields
            message = struct.pack('!IB', sequence_number, 0) + info

            sequence_number += 1
        
            # Combine the UDP header with the message
            datagram = udp_header + message

            print(f"datagram: {datagram}\n")
        
            # Send the datagram to the server
            self.UDP_socket.sendto(datagram, addr)
            #print(f"Datagram sent: Seq: {sequence_number}, Type: {message_type}, Data: {data.decode('utf-8')}")

    def parse_json(self, path: str):
        # Existing code for parsing JSON remains unchanged
        lista_tasks = Tasks()
        with open(path, "r") as file:
            tasks_json = json.load(file)

        for task in tasks_json:
            device_metrics = Device_metrics(
                task["Devices"]["devices_metric"]["cpu_usage"],
                task["Devices"]["devices_metric"]["ram_usage"],
                task["Devices"]["devices_metric"]["interface_stats"]
            )

            latency = task["Devices"]["link_metrics"]["latency"]
            if latency:
                latency_config = LatencyConfig(
                    True,
                    task["Devices"]["link_metrics"]["destination"],
                    task["Devices"]["link_metrics"]["packet_count"]
                )
            else:
                latency_config = LatencyConfig()

            link_metrics = Link_metrics(
                task["Devices"]["link_metrics"]["use_iperf"],
                task["Devices"]["link_metrics"]["server_address"],
                task["frequency"],
                task["Devices"]["link_metrics"]["bandwidth"],
                task["Devices"]["link_metrics"]["jitter"],
                task["Devices"]["link_metrics"]["packet_loss"],
                latency_config
            )

            alterflow = task["Devices"]["AlterFlowConditions"]["alterflow"]
            if alterflow:
                alterflow_conditions = AlterflowConditions(
                    True,
                    task["Devices"]["AlterFlowConditions"]["cpu_usage"],
                    task["Devices"]["AlterFlowConditions"]["ram_usage"],
                    task["Devices"]["AlterFlowConditions"]["interface_stats"],
                    task["Devices"]["AlterFlowConditions"]["packet_loss"],
                    task["Devices"]["AlterFlowConditions"]["jitter"]
                )
            else:
                alterflow_conditions = AlterflowConditions()

            config = Config(device_metrics, link_metrics, alterflow_conditions)

            task_obj = Task(self.lastTask, task["type"], task["frequency"], task["duration"], task["devices"], config)

            self.lastTask += 1
            lista_tasks.add_task(task_obj)

        id = 1
        while lista_tasks.get_task("T-" + str(id)):
            t = lista_tasks.get_task("T-" + str(id))
            print(t.task_id, t.type, t.devices)
            id += 1

        self.tasks = lista_tasks

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



    def listen_for_datagrams(self):
        buffer_size = 1024
        while not self._stop_event.is_set():
            try:
                print(f"Server listening:\n")
                data, addr = self.UDP_socket.recvfrom(buffer_size)
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
        payload = data.decode('utf-8')
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

            self.sendMessage(socket, client_addr,"Ack: " + "Port:"+str(port))



            if client_id and client_addr:
                # Converta a porta para inteiro e adicione o cliente
                #client = Client(client_id, server_ip, int(server_port))
                
                client = ClientServer(addr, socket)
                self.clients.add_client(client_id, client)
                print(f"Client {client_id} added with Address {client_addr}")
                print(f"{str(self.clients.to_dict())}\n")
            else:
                print("Erro: Dados do cliente ausentes ou incompletos na mensagem de registro.")
        else:
            # Processa outras mensagens
            print(f"Received non-registration data: {payload}")

    def close(self):
            self._stop_event.set()
            # Close the socket
            self.UDP_socket.close()
            self.TCP_socket.close()
