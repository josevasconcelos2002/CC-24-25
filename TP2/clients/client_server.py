class ClientServer:

    def __init__(self, addr, socket):
        self.address = addr
        self.socket = socket
        self.metrics = {}

    def to_dict(self):
        # Retorna os dados do cliente como um dicionário
        return {
            "address": self.address,
            "socket": self.socket,
            "metrics": self.metrics
        }
    
    def add_metric(self, task_id: str, metric: str):
        self.metrics[task_id] += metric