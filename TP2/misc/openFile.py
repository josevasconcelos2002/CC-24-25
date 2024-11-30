import os

def manage_file(task_id, device_id):
    # Define o caminho do armazenamento
    storage_path = "/home/core/Documents/storage"  # Ajuste conforme necessário

    # Verifica e cria o diretório de armazenamento, caso não exista
    if not os.path.exists(storage_path):
        os.makedirs(storage_path)

    # Verifica e cria o subdiretório com o nome do "task_id"
    task_dir = os.path.join(storage_path, str(task_id))
    if not os.path.exists(task_dir):
        os.makedirs(task_dir)

    # Define o nome do arquivo com base no device_id
    file_name = f"{device_id}.txt"
    file_path = os.path.join(task_dir, file_name)

    # Abre o arquivo em modo de anexação e o retorna
    with open(file_path, "a") as file:
        return file
