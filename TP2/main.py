from server.NMS_server import NMS_server
import os

if __name__ == "__main__":

    nms_server = NMS_server()


    current_dir = os.path.dirname(__file__)
    json_path = os.path.join(current_dir, "tasks.json")
    nms_server.parse_json(json_path)
    
