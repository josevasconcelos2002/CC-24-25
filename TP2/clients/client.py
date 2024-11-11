import socket
import struct
import uuid
from tasks.task import Task
<<<<<<< Updated upstream
=======
import threading
import time
import random
>>>>>>> Stashed changes

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
        udp_socket.bind(('127.0.0.'+ str(random.randint(2, 100)), random.randint(1, 65535)))
        return udp_socket
    

    def send_initial_info(self):
<<<<<<< Updated upstream
        # Serialize ID and other relevant client data
        message = f"ID:{self.id}".encode('utf-8')
        
        # Send this message to the server over UDP
        self.UDP_socket.sendto(message, (self.server_ip, self.server_port))
        print(f"Sent initial client info to server: {message.decode('utf-8')}")
=======
        while self.connected == False and not self._stop_event.is_set():
            # Serialize ID and other relevant client data
            message = f"ID:{self.id}"
        
            # Send this message to the server over UDP
            self.sendMessage(self.UDP_socket, (self.server_ip, self.server_port), message)
            print(f"Sent initial client info to server: {message}")
            time.sleep(0.5)
>>>>>>> Stashed changes
    
    def sendMessage(self, socket, addr, data):
        with self.lock:
            # Build the UDP datagram with the defined structure
            source_port = socket.getsockname()[1]  # Source port (can be configurable)
            dest_port = self.server_port

            data = data.encode('utf-8')

            chunk_size = 400
            chunks = [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]

            sequence_number = 0
            sequence_length = len(chunks)

            for info in chunks:

                # UDP header fields
                length = 13 + len(info)  # UDP header (8 bytes) + data
                checksum = 0  # Simulated, checksum calculation not implemented

                #print(f"source_port type: {type(source_port)}")
                #print(f"dest_port type: {type(dest_port)}")
                #print(f"length type: {type(length)}")
                #print(f"checksum type: {type(checksum)}")

                # Pack the UDP header fields
                udp_header = struct.pack('!HHHH', source_port, dest_port, length, checksum)
                # Pack additional protocol fields
                message = struct.pack('!II', sequence_number, sequence_length) + info

                sequence_number += 1
        
                # Combine the UDP header with the message
                datagram = udp_header + message

                print(f"datagram: {datagram}\n")
        
                # Send the datagram to the server
                print("here: "+str(addr)+str(self.server_port))
                self.UDP_socket.sendto(datagram, addr)
                #print(f"Datagram sent: Seq: {sequence_number}, Type: {message_type}, Data: {data.decode('utf-8')}")

<<<<<<< Updated upstream
=======


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

    def handle_datagram(self,data, addr):
        # Decodifique os dados recebidos de bytes para string
        print(f"Received raw data: {data}")
        payload = data[16:]
        payload = payload.decode('utf-8')  # 'ignore' skips invalid bytes
        headers = data[:len(payload)]
        print(f"Received data: {payload}\n")
        print(f"Adrr: {addr}\n")
        
        # Verifique se a mensagem contém um ID para processar os dados do cliente
        if payload.startswith("Ack"):
            server_info = payload.split(",")
            server_data = {}
            
            # Extraia pares chave:valor do payload
            for info in server_info:
                if ":" in info:
                    key, value = info.split(":", 1)  # Limite de divisão para capturar valores completos
                    print(value)
                    server_data[key.strip()] = value.strip()

            # Obtenha os dados do cliente e valide se todos os campos estão presentes
            with self.lock:        
                self.server_port = int(server_data.get("Port"))
                print(str(self.server_port)+" here")
                self.connected = True

        else:
            #with self.lock:
                time.sleep(3)
                self.sendMessage(self.UDP_socket, (self.server_ip, self.server_port), "Received")
                print(self.server_port)


>>>>>>> Stashed changes
    def to_dict(self):
        # Retorna os dados do cliente como um dicionário
        return {
            "id": self.id,
            "server_ip": self.server_ip,
            "server_port": self.server_port,
            "Tasks": self.Tasks
        }

    def close(self):
<<<<<<< Updated upstream
        # Close the socket
        self.UDP_socket.close()
=======
        with self.lock:
            self._stop_event.set()
            # Close the socket
            self.UDP_socket.close()
>>>>>>> Stashed changes
