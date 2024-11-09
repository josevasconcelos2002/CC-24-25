class ClientServer:

    def __init__(self, addr, socket):
        self.address = addr
        self.socket = socket

    def to_dict(self):
        # Retorna os dados do cliente como um dicionário
        return {
            "address": self.address,
            "socket": self.socket
        }