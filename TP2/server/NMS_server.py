import json
import socket
import struct
import threading
from tasks.config import Config, Device_metrics, AlterflowConditions, LatencyConfig, Link_metrics
from tasks.task import Task
from tasks.tasks import Tasks

class NMS_server:

    def __init__(self):
        self.lastTask = 1
        self.tasks = Tasks()
        self.UDP_socket = self.setup_UDP_socket()  # Initialize the UDP socket
        self.TCP_socket = self.setup_TCP_socket()  # Initialize the TCP socket
        self.threads = []

        for _ in range(4):
            thread = threading.Thread(target=self.worker)
            thread.start()
            self.thread_pool.append(thread)

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
        print("Servidor UDP aguardando mensagens...")
        buffer_size = 1024  # Buffer size to receive datagrams
        while True:
            data, addr = self.UDP_socket.recvfrom(buffer_size)
            self.handle_datagram(data, addr)  # Process the received datagram

    def handle_datagram(self, data, addr):
        # Unpack the datagram data, assuming the structure we discussed
        udp_header = struct.unpack('!HHHH', data[:8])  # Adjust according to your protocol
        source_port, dest_port, length, checksum = udp_header

        # Assuming you have sequence_number and message_type after
        sequence_number, message_type = struct.unpack('!IB', data[8:13])  # 32 bits for seq, 8 bits for type
        
        # The rest is the payload
        payload = data[13:]

        print(f"Recebido datagrama de {addr}:")
        print(f"Porta de origem: {source_port}, Porta de destino: {dest_port}, Comprimento: {length}, Checksum: {checksum}")
        print(f"Número de sequência: {sequence_number}, Tipo de mensagem: {message_type}, Dados: {payload.decode('utf-8')}")
