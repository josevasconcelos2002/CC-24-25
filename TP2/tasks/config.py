from dataclasses import dataclass
from typing import List, Dict
import json






class Device_metrics:
    cpu_usage: bool
    ram_usage: bool
    interface_stats: List[str] 

    def __init__(self, cpu_usage: bool, ram_usage: bool, interface_stats: List[str]):
        self.cpu_usage = cpu_usage
        self.ram_usage = ram_usage
        self.interface_stats = interface_stats

    def to_dict(self):
        return {
            "cpu_usage": self.cpu_usage,
            "ram_usage": self.ram_usage,
            "interface_stats": self.interface_stats
        }


class AlterflowConditions:
    alterflow_conditions: bool
    cpu_usage: int   # %
    ram_usage: int   # %
    interface_stats: int  #  pacotes por segundo (pps)
    packet_loss: int  # %
    jitter_limit: int  # e.g. 100 ms

    def __init__(self, alterflow_conditions=None, cpu_usage=None, ram_usage=None, interface_stats=None, packet_loss=None, jitter_limit=None):
        self.alterflow_conditions = alterflow_conditions if alterflow_conditions is not None else False
        self.cpu_usage = cpu_usage if cpu_usage is not None else 0
        self.ram_usage = ram_usage if ram_usage is not None else 0
        self.interface_stats = interface_stats if interface_stats is not None else 0
        self.packet_loss = packet_loss if packet_loss is not None else 0
        self.jitter_limit = jitter_limit if jitter_limit is not None else 0        

    def to_dict(self):
        return {
            "alterflow_conditions": self.alterflow_conditions,
            "cpu_usage": self.cpu_usage,
            "ram_usage": self.ram_usage,
            "interface_stats": self.interface_stats,
            "packet_loss": self.packet_loss,
            "jitter_limit": self.jitter_limit
        }    


    
class LatencyConfig:
    latency: bool
    destination: str
    packet_count: int

        
    def __init__(self, latency=None, destination=None, packet_count=None):
        self.latency = latency if latency is not None else False
        self.destination = destination if destination is not None else ""
        self.packet_count = packet_count if packet_count is not None else 0

    def to_dict(self):
        return {
            "latency": self.latency,
            "destination": self.destination,
            "packet_count": self.packet_count
        }    



class Link_metrics:
    use_iperf: bool
    server_address: str
    frequency: int
    bandwidth: bool
    jitter: bool
    packet_loss: bool
    latency: LatencyConfig

    def __init__(self, use_iperf: bool, server_address: str, frequency: int, bandwidth: bool, jitter: bool, packet_loss: bool, latency: LatencyConfig):
        self.use_iperf = use_iperf
        self.server_address = server_address
        self.frequency = frequency
        self.bandwidth = bandwidth
        self.jitter = jitter
        self.packet_loss = packet_loss
        self.latency = latency


    def to_dict(self):
        return {
            "use_iperf": self.use_iperf,
            "server_address": self.server_address,
            "frequency": self.frequency,
            "bandwidth": self.bandwidth,
            "jitter": self.jitter,
            "packet_loss": self.packet_loss,
            "latency": self.latency.to_dict()
        }    


class Config:
    device_metrics: Device_metrics
    link_metrics: Link_metrics
    alterflow_conditions: AlterflowConditions

    def __init__(self, device_metrics: Device_metrics, link_metrics: Link_metrics, alterflow_conditions: AlterflowConditions):
        self.device_metrics = device_metrics
        self.link_metrics = link_metrics
        self.alterflow_conditions = alterflow_conditions

    def to_dict(self):
        return {
            "device_metrics": self.device_metrics.to_dict(),
            "link_metrics": self.link_metrics.to_dict(),
            "alterflow_conditions": self.alterflow_conditions.to_dict()
        }