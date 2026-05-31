import json
import os

UDP_PORT = 8080

def load_node_config(node_id):
    path = os.path.join("network", f"{node_id}.json")

    if not os.path.isfile(path):
        raise FileNotFoundError(f"Config file not found: {path}")

    with open(path, "r") as f:
        return json.load(f)
