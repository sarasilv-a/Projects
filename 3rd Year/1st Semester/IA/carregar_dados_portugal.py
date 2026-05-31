import json
from Grafo import Grafo
from Vehicle import Vehicle
from Node import Node


def carregar_dados_portugal(file_path='portugal.json'):
    """
    Carrega os dados de um arquivo JSON especificado e cria o grafo e os veículos.
    :param file_path: Caminho do arquivo JSON a ser carregado.
    :return: Uma tupla (graph, vehicles) com o grafo e a lista de veículos.
    """
    graph = Grafo()
    vehicles = []

    try:
        # Carregar dados do JSON com especificação de codificação
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
    except FileNotFoundError:
        print(f"Erro: Arquivo '{file_path}' não encontrado.")
        return None, None
    except json.JSONDecodeError:
        print(f"Erro: Arquivo '{file_path}' está mal formatado.")
        return None, None

    # Validar estrutura do JSON
    if "veiculos" not in data or "nos" not in data or "arestas" not in data:
        raise ValueError("O arquivo JSON deve conter 'veiculos', 'nos' e 'arestas'.")

    # Criar veículos
    for v_data in data["veiculos"]:
        vehicle = Vehicle(
            name=v_data["nome"],
            peso=v_data["peso"],
            capacity=v_data["capacidade"],
            speed=v_data["velocidade"],
            fuel=v_data["combustivel"],
            fuel_efficiency=v_data["eficiencia_combustivel"]
        )
        vehicles.append(vehicle)

    # Criar nós (distritos)
    nodes = {}
    for n_data in data["nos"]:
        node = Node(
            name=n_data["nome"],
            id=n_data["id"],
            priority=n_data["prioridade"],
            suprimentosNecessarios=n_data["suprimentos_necessarios"]
        )
        # Definir acessibilidade com os nomes dos veículos
        accessible_vehicles = [
            v for v in vehicles if v.getName() in n_data["acessibilidade"]
        ]
        if not accessible_vehicles:
            print(f"Aviso: Nenhum veículo acessível encontrado para o nó {n_data['nome']}.")
        node.setAccessibility(accessible_vehicles)

        node.m_delivery_deadline = n_data.get("delivery_deadline", None)  # Valor padrão: None

        nodes[node.getName()] = node
        graph.add_node(node)

    # Criar arestas (distâncias entre distritos)
    for edge in data["arestas"]:
        origem = nodes.get(edge["origem"])
        destino = nodes.get(edge["destino"])
        custo = edge.get("custo")

        # Verificar se a origem e o destino são válidos
        if origem is None:
            print(f"Erro: A origem '{edge['origem']}' não existe.")
            continue
        if destino is None:
            print(f"Erro: O destino '{edge['destino']}' não existe.")
            continue
        if custo is None:
            print(f"Erro: A aresta entre '{edge['origem']}' e '{edge['destino']}' não tem custo definido.")
            continue

        graph.add_edge(origem, destino, custo)

    print("Dados carregados com sucesso!")
    return graph, vehicles
