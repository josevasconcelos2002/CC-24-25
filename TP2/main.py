from server.NMS_server import NMS_server
from clients.client import Client
import os
import time
import threading

if __name__ == "__main__":
    # Initialize the NMS server
    nms_server = NMS_server()

    # Load tasks from JSON
    current_dir = os.path.dirname(__file__)
    json_path = os.path.join(current_dir, "tasks.json")
    nms_server.parse_json(json_path)


    # Start the server in a separate thread
    server_thread = threading.Thread(target=nms_server.listen_for_datagrams)
    server_thread.start()

    # Give the server a moment to start up
    time.sleep(1)

    # Create a UDP client instance
    client = Client(server_ip='127.0.0.1', server_port=54321)
    client.send_initial_info()

    """
    # Example of sending a datagram
    sequence_number = 1
    message_type = 1  # Example message type
    data = b'Hello, this is a test message.'  # Data to be sent

    client.send_UDP_datagram(sequence_number, message_type, data)

    # Close the client socket
    """
    client.close()

    # Optionally, you can join the server thread if needed
    server_thread.join()
