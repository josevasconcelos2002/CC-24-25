from server.NMS_server import NMS_server

if __name__ == "__main__":

    nms_server = NMS_server()

    nms_server.parse_json("task.json")    # começamos por fazer parsing do ficheiro json
    
