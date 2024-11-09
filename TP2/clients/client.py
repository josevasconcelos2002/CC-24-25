import socket
import struct
import uuid
from tasks.task import Task
import threading
import time

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

    def setTask(self,task: Task):
        self.Task = task



    def setup_UDP_socket(self):
        # Create a UDP socket
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return udp_socket
    

    def send_initial_info(self):
        while self.connected == False:
            # Serialize ID and other relevant client data
            message = f"ID:{self.id}".encode('utf-8')
        
            # Send this message to the server over UDP
            self.UDP_socket.sendto(message, (self.server_ip, self.server_port))
            print(f"Sent initial client info to server: {message.decode('utf-8')}")
            time.sleep(0.5)
    
    def send_UDP_datagram(self, sequence_number: int, message_type: int, data: bytes):
        # Build the UDP datagram with the defined structure
        source_port = 54321  # Source port (can be configurable)
        dest_port = self.server_port

        # UDP header fields
        length = 8 + len(data)  # UDP header (8 bytes) + data
        checksum = 0  # Simulated, checksum calculation not implemented

        # Pack the UDP header fields
        udp_header = struct.pack('!HHHH', source_port, dest_port, length, checksum)
        # Pack additional protocol fields
        message = struct.pack('!IB', sequence_number, message_type) + data
        
        # Combine the UDP header with the message
        datagram = udp_header + message
        
        # Send the datagram to the server
        self.UDP_socket.sendto(datagram, (self.server_ip, self.server_port))
        #print(f"Datagram sent: Seq: {sequence_number}, Type: {message_type}, Data: {data.decode('utf-8')}")



    def listen_for_datagrams(self):
        buffer_size = 1024
        while not self._stop_event.is_set():
            try:
                print(f"Client listening:\n")
                data, addr = self.UDP_socket.recvfrom(buffer_size)
                if data:
                    self.server_port = addr[1]
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
        payload = data[13:]
        payload = payload.decode('utf-8')  # 'ignore' skips invalid bytes
        headers = data[:len(payload)]
        print(f"Received data: {payload}\n")
        print(f"Adrr: {addr}\n")
        
        # Verifique se a mensagem contém um ID para processar os dados do cliente
        if payload.startswith("Ack:"):
            server_info = payload.split(",")
            server_data = {}
            
            # Extraia pares chave:valor do payload
            for info in server_info:
                if ":" in info:
                    key, value = info.split(":", 1)  # Limite de divisão para capturar valores completos
                    server_data[key.strip()] = value.strip()

            # Obtenha os dados do cliente e valide se todos os campos estão presentes
            with self.lock:        
                self.server_port = server_data.get("Port")
                self.connected = True



    def to_dict(self):
        # Retorna os dados do cliente como um dicionário
        return {
            "id": self.id,
            "server_ip": self.server_ip,
            "server_port": self.server_port,
            "Tasks": self.Tasks
        }

    def close(self):
        self._stop_event.set()
        # Close the socket
        self.UDP_socket.close()
