import socket
import struct 

def sendMessage(socket, addr, data, messageType):
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
            length = 14 + len(info)  # UDP header (8 bytes) + data
            checksum = 0  # Simulated, checksum calculation not implemented

            # Pack the UDP header fields
            udp_header = struct.pack('!HHHHH', source_port, dest_port, length, checksum, messageType)
            # Pack additional protocol fields
            message = struct.pack('!HH', sequence_number, sequence_length) + info

            sequence_number += 1
        
            # Combine the UDP header with the message
            datagram = udp_header + message

            #print(f"datagram: {datagram}\n")
        
            # Send the datagram to the server
            socket.sendto(datagram, addr)
            #print(f"Datagram sent: Seq: {sequence_number}, Type: {message_type}, Data: {data.decode('utf-8')}")