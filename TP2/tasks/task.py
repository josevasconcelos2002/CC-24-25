from dataclasses import dataclass
import pickle
from typing import List, Dict
import json

from tasks.config import Config


@dataclass
class Task:
    
    def __init__(self, id: int, type: str, frequency: int, duration: int, devices: List[str], config: Config):
        
        self.task_id = "T-" + str(id)
        self.type = type
        self.frequency = frequency
        self.duration = duration
        self.devices = devices
        self.config = config 


    def getDevices(self):
        return self.devices

    def to_dict(self):
        return {
            "task_id": self.task_id,
            "type": self.type,
            "frequency": self.frequency,
            "duration": self.duration,
            "devices": self.devices,
            "Devices": self.config.to_dict()
        }

    def to_bytes(self):
        # Convert task to dictionary, then to JSON string
        return json.dumps(self.to_dict())
    
    # tranforma a instancia do objeto Task em binario
    def serialize(self):
        return pickle.dumps(self)
    
    # Desserializa os dados binários para criar uma nova instância de Task
    @classmethod
    def deserialize(cls, data):
        return pickle.loads(data)