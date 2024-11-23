from server.NMS_server import NMS_server
from clients.client import Client
import os
import time
import threading
import sys

if __name__ == "__main__":
    # sys.argv[1:] contém os argumentos passados ao script
    if len(sys.argv) < 1:
        print("Usage: python script_name.py <arg1>")
        sys.exit(1)

    arg1 = sys.argv[1]  # Primeiro argumento

    print(f"Argumento 1: {arg1}")

    server_ip='0.0.0.0'
    server_port=54321
    
    client1 = Client(server_ip, server_port, arg1 )
    client1_thread = threading.Thread(target=client1.listen_for_datagrams)
    client1_thread.daemon = True
    client1_thread.start()

    client1.send_initial_info()

    time.sleep(20)

    


    client1.close()
    
    client1_thread.join()


