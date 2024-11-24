import shutil
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

    server_ip='0.0.0.0'
    server_port=54321


    # Start the server in a separate thread
    server_thread = threading.Thread(target=nms_server.listen_for_datagrams, args=(nms_server.UDP_socket,))
    server_thread.daemon = True
    server_thread.start()

    time.sleep(20)
    
    storage_path = "storage"
    if os.path.exists(storage_path):
        shutil.rmtree(storage_path)  # Remove o diretório e todo o seu conteúdo
        print(f'Diretório "{storage_path}" e seu conteúdo foram removidos.')