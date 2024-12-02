from tasks.task import Task
from tasks.config import AlterflowConditions, Config, Device_metrics, LatencyConfig, Link_metrics




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

    alterflow = task["Devices"]["AlterFlowConditions"]["alterflow"]
    if alterflow:
        alterflow_conditions = AlterflowConditions(
            True,
            task["Devices"]["AlterFlowConditions"]["cpu_usage"],
            task["Devices"]["AlterFlowConditions"]["ram_usage"],
            task["Devices"]["AlterFlowConditions"]["interface_stats"],
            task["Devices"]["AlterFlowConditions"]["packet_loss"],
            task["Devices"]["AlterFlowConditions"]["jitter"]
        )
    else:
        alterflow_conditions = AlterflowConditions()

    config = Config(device_metrics, link_metrics, alterflow_conditions)

    task_obj = Task(lastTask, task["type"], task["frequency"], task["duration"], task["devices"], config)
    return task_obj