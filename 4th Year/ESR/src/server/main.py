import argparse
from server import Server
from config import load_node_config


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--id", required=True)
    args = parser.parse_args()

    config = load_node_config(args.id)

    server = Server(config)

    # DEBUG EARLY MESSAGE
    print("Loaded server:")
    print(" id:", server.node_id)
    print(" role:", server.role)
    print(" neighbors:", server.neighbors)
    print(" streams:", server.stream_ids)

    server.run()

if __name__ == "__main__":
    main()
