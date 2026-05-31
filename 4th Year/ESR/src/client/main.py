import argparse
from client import Client
from config import load_node_config

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--id", required=True)
    args = parser.parse_args()

    config = load_node_config(args.id)

    client = Client(config)

    # DEBUG EARLY MESSAGE
    print("Loaded client:")
    print(" id:", client.client_id)

    client.join_network()
    client.menu_loop()

if __name__ == "__main__":
    main()
