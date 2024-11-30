import os

def openFile( task_id, device_id):
        
        storage_path = "/home/core/Documents/storage"  
        #storage_path = "storage"
        if not os.path.exists(storage_path):
            os.makedirs(storage_path)
        

        task_dir = os.path.join(storage_path, str(task_id))
        if not os.path.exists(task_dir):
            os.makedirs(task_dir)

        file_name = f"{device_id}.txt"
        file_path = os.path.join(task_dir, file_name)

        file = open(file_path, "a")
        return file