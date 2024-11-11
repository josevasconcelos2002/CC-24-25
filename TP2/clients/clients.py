import json
from .client_server import ClientServer


class Clients:
    def __init__(self):

        self.clients = {}

    def __len__(self):
        return len(self.clients)

    def add_client(self, id,client: ClientServer):

        self.clients[id] = client

    def remove_client(self, id: str):

        if id in self.clients:
            del self.clients[id]

    def get_client(self, id: str) -> ClientServer:

        return self.clients.get(id)
    
    def to_dict(self):

        return {id: client.to_dict() for id, client in self.clients.items()}
    
    def __str__(self):
        # Converte o dicionário de tarefas para uma string JSON formatada
        return json.dumps(self.to_dict(), indent=4)

    def __iter__(self):
    # Make the class iterable by returning an iterator over self.clients.items()
        return iter(self.clients.items())