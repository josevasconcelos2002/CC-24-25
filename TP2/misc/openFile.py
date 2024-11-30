    def write_info(self, task_id, device_id):
        
        storage_path = "/home/core/Downloads/CC-24-25-main/TP2/storage"  # utilizar um path parecido no core
        #storage_path = "storage"
        if not os.path.exists(storage_path):
            os.makedirs(storage_path)
        
        # Verifica e cria o subdiretÃ³rio com o nome do "task_id"
        task_dir = os.path.join(storage_path, str(task_id))
        if not os.path.exists(task_dir):
            os.makedirs(task_dir)

        file_name = f"{device_id}.txt"
        file_path = os.path.join(task_dir, file_name)

        file = open(file_path, "a")
        return file