from tasks.task import Task
from tasks.config import AlertflowConditions, Config, Device_metrics, LatencyConfig, Link_metrics




def parseTasks(lastTask, task):
    device_metrics = Device_metrics(
        task["Devices"]["devices_metric"]["cpu_usage"],
        task["Devices"]["devices_metric"]["ram_usage"],
        task["Devices"]["devices_metric"]["interface_stats"]
    )

    latency = task["Devices"]["link_metrics"]["latency"]
    if latency:
        latency_config = LatencyConfig(
            True,
            task["Devices"]["link_metrics"]["packet_count"]
        )
    else:
        latency_config = LatencyConfig()

    link_metrics = Link_metrics(
        task["Devices"]["link_metrics"]["use_iperf"],
        task["Devices"]["link_metrics"]["server"],
        task["Devices"]["link_metrics"]["duration"],
        task["Devices"]["link_metrics"]["server_address"],
        task["frequency"],
        task["Devices"]["link_metrics"]["bandwidth"],
        task["Devices"]["link_metrics"]["jitter"],
        task["Devices"]["link_metrics"]["packet_loss"],
        latency_config
    )

    alertflow = task["Devices"]["AlertFlowConditions"]["alertflow"]
    if alertflow:
        alertflow_conditions = AlertflowConditions(
            True,
            task["Devices"]["AlertFlowConditions"]["cpu_usage"],
            task["Devices"]["AlertFlowConditions"]["ram_usage"],
            task["Devices"]["AlertFlowConditions"]["interface_stats"],
            task["Devices"]["AlertFlowConditions"]["packet_loss"],
            task["Devices"]["AlertFlowConditions"]["jitter"]
        )
    else:
        alertflow_conditions = AlertflowConditions()

    config = Config(device_metrics, link_metrics, alertflow_conditions)

    task_obj = Task(lastTask, task["type"], task["frequency"], task["duration"], task["devices"], config)
    return task_obj