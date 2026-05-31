import argparse
from transport.node import Node
from config import load_node_config

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--id", required=True)
    args = parser.parse_args()

    config = load_node_config(args.id)

    node = Node(config)

    # DEBUG EARLY MESSAGE
    print("Loaded node:")
    print(" id:", node.node_id)
    print(" role:", node.role)
    print(" neighbors:", node.neighbors)
    node.run()


if __name__ == "__main__":
    main()
