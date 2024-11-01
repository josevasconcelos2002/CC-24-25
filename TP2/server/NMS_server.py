


import json

from tasks.config import Config, Device_metrics, AlterflowConditions, LatencyConfig, Link_metrics

from tasks.task import Task
from tasks.tasks import Tasks


class NMS_server:

    def __init__ (self):
        self.lastTask = 1
        self.tasks = Tasks()

    def parse_json(self,path: str):

        lista_tasks = Tasks()

        with open(path, "r") as file:
            tasks_json = json.load(file)

        for task in tasks_json:
            device_metrics = Device_metrics(
               task["Devices"]["devices_metric"]["cpu_usage"],
               task["Devices"]["devices_metric"]["ram_usage"],
               task["Devices"]["devices_metric"]["interface_stats"]
            )

            latency = task["Devices"]["link_metrics"]["latency"]
            if latency == True:
                latency_config = LatencyConfig(
                                    True,
                                    task["Devices"]["link_metrics"]["destination"], 
                                    task["Devices"]["link_metrics"]["packet_count"])
            else:
                latency_config = LatencyConfig()

            link_metrics = Link_metrics(
                                   task["Devices"]["link_metrics"]["use_iperf"], 
                                   task["Devices"]["link_metrics"]["server_address"], 
                                   task["frequency"], 
                                   task["Devices"]["link_metrics"]["bandwidth"], 
                                   task["Devices"]["link_metrics"]["jitter"], 
                                   task["Devices"]["link_metrics"]["packet_loss"], 
                                   latency_config)

            alterflow = task["Devices"]["AlterFlowConditions"]["alterflow"]
            if alterflow == True:
                alterflow_conditions = AlterflowConditions(
                                             True,
                                             task["Devices"]["AlterFlowConditions"]["cpu_usage"], 
                                             task["Devices"]["AlterFlowConditions"]["ram_usage"], 
                                             task["Devices"]["AlterFlowConditions"]["interface_stats"], 
                                             task["Devices"]["AlterFlowConditions"]["packet_loss"], 
                                             task["Devices"]["AlterFlowConditions"]["jitter"])
            else:
                alterflow_conditions = AlterflowConditions()

            config = Config(device_metrics, link_metrics, alterflow_conditions)

            task = Task(self.lastTask, task["type"], task["frequency"], task["duration"], task["devices"], config)

            self.lastTask +=  1

            lista_tasks.add_task(task)
        
        id = 1
        while lista_tasks.get_task("T-"+str(id)):
            t = lista_tasks.get_task("T-"+str(id))
            print(t.task_id, t.type, t.devices)
            id += 1

        self.tasks = lista_tasks

        #task_objects = [Task(self.lastTask, task["type"], task["frequency"], task["duration"], task["devices"], Config(Device_metrics(task["cpu_usage"], task["ram_usage", task["interface_stats"]]), Link_metrics(task[]))) for task in tasks_json]

        #for task in task_objects:
            #lista_tasks.add_task(task)