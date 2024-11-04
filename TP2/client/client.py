import socket
import struct
import uuid

class Client: 

    def __init__(self, server_ip: str, server_port: int):
        self.id = str(uuid.uuid4()) # generates a random id
        self.server_ip = server_ip
        self.server_port = server_port
        self.UDP_socket = self.setup_UDP_socket()
        self.TCP_socket = None    # socket TCP so e criado quando necessario


    def setup_UDP_socket(self):
        # Create a UDP socket
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return udp_socket
    
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
        self.socket.sendto(datagram, (self.server_ip, self.server_port))
        print(f"Datagram sent: Seq: {sequence_number}, Type: {message_type}, Data: {data.decode('utf-8')}")

    def close(self):
        # Close the socket
        self.socket.close()
