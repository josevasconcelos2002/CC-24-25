import json
from .client import Client


class Clients:
    def __init__(self):

        self.clients = {}

    def add_client(self, client: Client):

        self.clients[client.id] = client

    def remove_client(self, id: str):

        if id in self.clients:
            del self.clients[id]

    def get_client(self, id: str) -> Client:

        return self.clients.get(id)
    
    def to_dict(self):

        return {id: client.to_dict() for id, client in self.clients.items()}
    
    def __str__(self):
        # Converte o dicionário de tarefas para uma string JSON formatada
        return json.dumps(self.to_dict(), indent=4)