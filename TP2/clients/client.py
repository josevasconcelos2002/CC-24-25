import socket
import struct
import uuid
from tasks.task import Task

class Client: 

    def __init__(self, server_ip: str, server_port: int, client_id: str = None):
        # Se o client_id não for fornecido, gera um ID aleatório
        self.id = client_id if client_id else str(uuid.uuid4())
        self.server_ip = server_ip
        self.server_port = server_port
        self.UDP_socket = self.setup_UDP_socket()
        self.TCP_socket = None  # socket TCP só é criado quando necessário
        self.Tasks = []

    def setTask(self,task: Task):
        self.Task = task



    def setup_UDP_socket(self):
        # Create a UDP socket
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return udp_socket
    

    def send_initial_info(self):
        # Serialize ID and other relevant client data
        message = f"ID:{self.id},ServerIP:{self.server_ip},ServerPort:{self.server_port}".encode('utf-8')
        
        # Send this message to the server over UDP
        self.UDP_socket.sendto(message, (self.server_ip, self.server_port))
        print(f"Sent initial client info to server: {message.decode('utf-8')}")
    
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

    def to_dict(self):
        # Retorna os dados do cliente como um dicionário
        return {
            "id": self.id,
            "server_ip": self.server_ip,
            "server_port": self.server_port,
            "Tasks": self.Tasks
        }

    def close(self):
        # Close the socket
        self.UDP_socket.close()
