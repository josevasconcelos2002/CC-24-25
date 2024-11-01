from dataclasses import dataclass
from typing import List, Dict

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


    def to_dict(self):

        return {
            "task_id": self.task_id,
            "frequency": self.frequency,
            "devices": self.devices
        }