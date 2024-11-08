import json
import socket
import struct
import threading
from tasks.config import Config, Device_metrics, AlterflowConditions, LatencyConfig, Link_metrics
from tasks.task import Task
from tasks.tasks import Tasks
from clients.clients import Clients
from clients.client import Client

class NMS_server:

    def __init__(self):
        self.lastTask = 1
        self.tasks = Tasks()
        self.clients = Clients()
        self.UDP_socket = self.setup_UDP_socket()  # Initialize the UDP socket
        self.TCP_socket = self.setup_TCP_socket()  # Initialize the TCP socket
        self.threads = []

        # Inicia uma thread para escutar clientes UDP
        udp_thread = threading.Thread(target=self.listen_for_datagrams)
        udp_thread.start()
        self.threads.append(udp_thread)

    def setup_UDP_socket(self):
        # Creates a UDP socket
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_socket.bind(('127.0.0.1', 54321))  # Bind to localhost and a specified port
        return udp_socket
    
    def setup_TCP_socket(self):
        # Creates a TCP socket
        TCP_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        TCP_socket.bind(('127.0.0.1', 54322))
        return TCP_socket


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

    def listen_for_datagrams(self):
        print("Servidor UDP aguardando mensagens...\n")
        buffer_size = 1024  # Buffer size to receive datagrams
        while True:
            data, addr = self.UDP_socket.recvfrom(buffer_size)
            self.handle_datagram(data, addr)  # Process the received datagram

    def handle_datagram(self,data, addr):
        # Decodifique os dados recebidos de bytes para string
        payload = data.decode('utf-8')
        print(f"Received data: {payload}\n")

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
            server_ip = client_data.get("ServerIP")
            server_port = client_data.get("ServerPort")

            if client_id and server_ip and server_port:
                # Converta a porta para inteiro e adicione o cliente
                #client = Client(client_id, server_ip, int(server_port))
                
                client = Client(server_ip, int(server_port), client_id)
                self.clients.add_client(client)
                print(f"Client {client.id} added with IP {client.server_ip}, Port {client.server_port}")
                print(f"{str(self.clients.to_dict())}\n")
            else:
                print("Erro: Dados do cliente ausentes ou incompletos na mensagem de registro.")
        else:
            # Processa outras mensagens
            print(f"Received non-registration data: {payload}")
