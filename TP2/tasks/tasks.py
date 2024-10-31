import json
from .task import Task


class Tasks:
    def __init__(self):
        """
        Inicializa a coleção de tarefas como um dicionário vazio.
        """
        self.tasks = {}

    def add_task(self, task: Task):
        """
        Adiciona uma tarefa ao dicionário de tarefas.

        :param task: Objeto da classe Task a ser adicionado.
        """
        self.tasks[task.task_id] = task

    def remove_task(self, task_id: str):
        """
        Remove uma tarefa do dicionário com base no ID da tarefa.

        :param task_id: ID da tarefa a ser removida.
        """
        if task_id in self.tasks:
            del self.tasks[task_id]

    def get_task(self, task_id: str) -> Task:
        """
        Retorna uma tarefa pelo seu ID.

        :param task_id: ID da tarefa a ser recuperada.
        :return: Objeto Task correspondente ao ID fornecido.
        """
        return self.tasks.get(task_id)
    
    def to_dict(self):
        """
        Converte todas as tarefas em um dicionário para fácil serialização em JSON.
        
        :return: Dicionário com todas as tarefas.
        """
        return {task_id: task.to_dict() for task_id, task in self.tasks.items()}
    
    def __str__(self):
        # Converte o dicionário de tarefas para uma string JSON formatada
        return json.dumps(self.to_dict(), indent=4)