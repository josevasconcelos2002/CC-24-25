from dataclasses import dataclass
from typing import List, Dict

from devices.device import AlterflowConditions, Device_metrics, Link_metrics





@dataclass
class Device_metrics:
    cpu_usage: bool
    ram_usage: bool
    interface_stats: List[str] 

    def Device



@dataclass
class AlterflowConditions:
    cpu_usage: int   # %
    ram_usage: int   # %
    interface_stats: int  #  pacotes por segundo (pps)
    packet_loss: int  # %
    jitter_limit: int  # e.g. 100 ms

    def AlterflowConditions(self):
        self.cpu_usage = 0




    
class LatencyConfig:
    latency: bool
    destination: str
    packet_count: int


    def LatencyConfig(self):
        self.latency = False
        self.destination = ""
        self.packet_count = 0
        
    def LatencyConfig(self, destination: str, packet_count: int):
        self.latency = True
        self.destination = destination
        self.packet_count = packet_count




@dataclass
class Link_metrics:
    use_iperf: bool
    server_address: str
    frequency: int
    bandwidth: bool
    jitter: bool
    packet_loss: bool
    latency: LatencyConfig


@dataclass
class Config:
    device_metrics: Device_metrics
    link_metrics: Link_metrics
    alterflow_conditions: AlterflowConditions
