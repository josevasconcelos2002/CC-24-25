from dataclasses import dataclass
from os import system
import os

@dataclass
class Menu:

    def __init__(self, storage_path):
        self.storage_path = storage_path

    def run(self):
        
        while True:
            print('''
                Bem-vindo!
            
                [1]- Introduza um task_id
                [0]- Sair
                ''')
            option = str(input("\nEscolha uma opção: "))

            if option == "1":
                task_id = str(input("\nIntroduza o task_id: "))

                task_id_normalized = "T-" + task_id

                #se existir, pedir para introduzir um device_id
                task_path = os.path.join(self.storage_path, task_id_normalized)
                if os.path.isdir(task_path):
                    print(f"A pasta '{task_id_normalized}' existe em '{self.storage_path}'!")

                    device_id = str(input("\nIntroduza o device_id: "))
                    device_id_normalized = "n" + device_id

                    files_in_directory = os.listdir(task_path)  # Lista todos os ficheiros na pasta
                    if device_id_normalized in files_in_directory:  # Verifica se o device_id está na lista de ficheiros
                        print(f"O ficheiro '{device_id_normalized}' existe em '{task_path}'!")
                    else:
                        print(f"O ficheiro '{device_id_normalized}' não existe em '{task_path}'.")
                else:
                    print(f"A pasta '{task_id_normalized}' não existe em '{self.storage_path}'.")

                #se nao existir, pedir para introduzir outra vez
                


            elif option == "0":
                system.exit(0)