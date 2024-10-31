


import json

import Config
from ..tasks.task import Task
from ..tasks.tasks import Tasks


class NMS_server:

    lastTask = 0

    def parse_json(self,path: str):

        lista_tasks = Tasks()

        with open(path, "r") as file:
            tasks_json = json.load(file)

        task_objects = [Task(self.lastTask, task["type"], task["frequency"], task["duration"], task["devices"], Config(Device_metrics(task["cpu_usage"], task["ram_usage", task["interface_stats"]]), Link_metrics(task[]))) for task in tasks_json]

        for task in task_objects:
            lista_tasks.add_task(task)