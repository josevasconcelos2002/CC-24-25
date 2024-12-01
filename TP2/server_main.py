import shutil
from server.NMS_server import NMS_server
from clients.client import Client
import os
import time
import threading
import sys

if __name__ == "__main__":
    # Verifica se o argumento foi fornecido
    if len(sys.argv) < 2:  # sys.argv[1] espera o argumento 1 como storage_path
        print("Necessita de fornecer o storage_path!")
        sys.exit(1)

    # Obter e ajustar o caminho do storage_path
    storage_path = sys.argv[1]
    if not storage_path.endswith("/storage"):
        storage_path = os.path.join(storage_path, "storage")
    print(f"Storage_path ajustado: {storage_path}")

    # Inicializar o servidor NMS
    nms_server = NMS_server(storage_path)

    # Carregar tarefas do JSON
    current_dir = os.path.dirname(__file__)
    json_path = os.path.join(current_dir, "tasks.json")
    nms_server.parse_json(json_path)

    # Configuração de IP e porta do servidor
    server_ip = '0.0.0.0'
    server_port = 54321

    # Iniciar o servidor em uma thread separada
    server_thread = threading.Thread(target=nms_server.listen_for_datagrams, args=(nms_server.UDP_socket,))
    server_thread.daemon = True
    server_thread.start()
    
    server1_thread = threading.Thread(target=nms_server.listen_TCP, args=(nms_server.TCP_socket,))
    server1_thread.daemon = True
    server1_thread.start()

    # Tempo de execução
    time.sleep(150)
