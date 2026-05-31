import heapq
import random

import matplotlib.pyplot as plt
from queue import Queue
import networkx as nx


class Grafo:
    def __init__(self, directed=False):
        self.directed = directed
        self.nodes = {}
        self.graph = {}  # Grafo como um dicionário de dicionários

    def add_node(self, node):
        if node.getId() not in self.nodes:
            self.nodes[node.getId()] = {
                'node': node,
                'edges': {}
            }
            self.graph[node.getId()] = {}  # Adiciona o nó ao grafo (dicionário de nós)

    def add_edge(self, from_node, to_node, cost):
        if from_node.getId() in self.nodes and to_node.getId() in self.nodes:
            self.nodes[from_node.getId()]['edges'][to_node.getId()] = cost
            if not self.directed:
                self.nodes[to_node.getId()]['edges'][from_node.getId()] = cost
            self.graph[from_node.getId()][to_node.getId()] = cost  # Adiciona aresta ao grafo

    def desenha(self):
        # Desenhando o grafo com matplotlib, usando um layout simples
        G = nx.Graph()

        for node_id, data in self.nodes.items():
            G.add_node(data['node'].getName())
            for neighbor_id, cost in data['edges'].items():
                neighbor_node = self.nodes[neighbor_id]['node']
                G.add_edge(data['node'].getName(), neighbor_node.getName(), weight=cost)

        # Layout dos nós com ajustes para afastar mais os nós
        pos = nx.spring_layout(G, k=0.2, iterations=50,
                               scale=2)  # Aumenta o valor de k e scale para afastar mais os nós

        # Espelhamento do grafo (invertendo a coordenada y)
        for node in pos:
            x, y = pos[node]
            pos[node] = (x, -y)  # Inverte a coordenada y (espelhamento vertical)

        # Desenha o grafo com as novas posições
        nx.draw(G, pos, with_labels=True, font_weight='bold', node_size=500, node_color='lightgreen', font_size=8)
        labels = nx.get_edge_attributes(G, 'weight')
        nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)

        plt.title("Grafo com Nós Afastados e Espelhado Verticalmente")
        plt.axis('off')  # Desativa os eixos
        plt.show()

    def find_node_by_name(self, name):
        name = str(name).lower()  # Certifica-se de que `name` seja uma string
        for data in self.nodes.values():
            if data['node'].getName().lower() == name:
                return data['node']
        return None

    def find_node_by_id(self, node_id):
        node_data = self.nodes.get(node_id)  # Busca pelo ID no dicionário `self.nodes`
        return node_data['node'] if node_data else None

    def calculate_path_cost(self, path):
        total_cost = 0
        for i in range(len(path) - 1):
            from_node = self.find_node_by_name(path[i])
            to_node = self.find_node_by_name(path[i + 1])

            if from_node and to_node:
                cost = self.nodes[from_node.getId()]['edges'].get(to_node.getId())
                if cost is not None:
                    total_cost += cost
                else:
                    print(f"Aresta não encontrada entre {path[i]} e {path[i + 1]}.")
                    return None
            else:
                print(f"Nó não encontrado: {path[i]} ou {path[i + 1]}.")
                return None

        return total_cost

    def get_neighbors(self, node):
        if node.getId() in self.nodes:
            return self.nodes[node.getId()]['edges']
        return None

    def getWeatherImpact(self, node):
        weather = node.getWeather().lower()
        impact_factors = {
            "ensolarado": 1.0,  # Sem impacto
            "nublado": 0.9,  # Impacto leve
            "chuva": 0.7,  # Impacto moderado
            "muito chuvoso": 0.5,  # Impacto forte
            "neve": 0.4,  # Impacto muito forte
            "desastre ambiental": 0.0  # Inacessível
        }

        return impact_factors.get(weather, 1.0)

    def procura_DFS(self, start_name, goal_name, path=None, visited=None, custo_acumulado=0):
        if path is None:
            path = []
        if visited is None:
            visited = set()

        # Caso base: se o ponto de partida é igual ao destino
        if start_name == goal_name:
            path.append(start_name)
            return path, custo_acumulado

        # Converte o nome do nó para o objeto do nó
        start = self.find_node_by_name(start_name)
        if not start:
            print(f"Erro: Nó '{start_name}' não encontrado.")
            return None, float('inf')

        # Marca o nó atual como visitado
        visited.add(start_name)
        path.append(start_name)  # Adiciona o nome do nó atual ao caminho

        # Explora os vizinhos
        for neighbor_id, peso in self.get_neighbors(start).items():
            neighbor_name = self.nodes[neighbor_id]['node'].getName()
            if neighbor_name not in visited:
                # Passa o custo acumulado ao vizinho
                result, custo = self.procura_DFS(
                    neighbor_name, goal_name, path, visited, custo_acumulado + peso
                )
                if result:
                    return result, custo

        # Retrocede no caminho (backtracking)
        path.pop()
        return None, float('inf')

    def procura_BFS(self, start_name, end_name):
        # Converte os nomes para objetos de nós
        start = self.find_node_by_name(start_name)
        end = self.find_node_by_name(end_name)

        if not start or not end:
            print(f"Erro: Nó '{start_name}' ou '{end_name}' não encontrado.")
            return None, None

        visited = set()
        fila = Queue()
        fila.put(start_name)
        visited.add(start_name)
        parent = {start_name: None}

        path_found = False
        while not fila.empty() and not path_found:
            nodo_atual_name = fila.get()

            if nodo_atual_name == end_name:
                path_found = True
            else:
                nodo_atual = self.find_node_by_name(nodo_atual_name)
                for neighbor_id, peso in self.get_neighbors(nodo_atual).items():
                    neighbor_name = self.nodes[neighbor_id]['node'].getName()
                    if neighbor_name not in visited:
                        fila.put(neighbor_name)
                        parent[neighbor_name] = nodo_atual_name
                        visited.add(neighbor_name)

        path = []
        if path_found:
            current = end_name
            while current is not None:
                path.append(current)
                current = parent[current]
            path.reverse()

            custo = self.calculate_path_cost(path)
            return path, custo

        return None, None

    def busca_custo_uniforme(self, inicio_nome, fim_nome):
        inicio = self.find_node_by_name(inicio_nome)
        fim = self.find_node_by_name(fim_nome)

        if not inicio or not fim:
            print("Erro: Nó inicial ou final não encontrado.")
            return None, 0

        fila_prioridade = [(0, inicio, [])]
        visitados = set()

        while fila_prioridade:
            custo, no_atual, caminho = heapq.heappop(fila_prioridade)

            if no_atual.getId() in visitados:
                continue
            visitados.add(no_atual.getId())

            caminho = caminho + [no_atual.getName()]
            if no_atual == fim:
                return caminho, custo

            for vizinho_id, distancia in self.get_neighbors(no_atual).items():
                vizinho = self.nodes[vizinho_id]['node']
                if vizinho_id not in visitados:
                    novo_custo = custo + distancia
                    heapq.heappush(fila_prioridade, (novo_custo, vizinho, caminho))

        print("Caminho não encontrado.")
        return None, 0

    def busca_bidirecional(self, inicio_nome, fim_nome):
        # Encontrar os nós de início e fim
        inicio = self.find_node_by_name(inicio_nome)
        fim = self.find_node_by_name(fim_nome)

        if not inicio or not fim:
            return None, float('inf')

        # Filas de prioridade para expandir as fronteiras
        fronteira_inicio = [(0, inicio, [inicio.getName()])]
        fronteira_fim = [(0, fim, [fim.getName()])]

        # Dicionários para armazenar custo acumulado e caminho visitado
        visitados_inicio = {inicio.getId(): (0, [inicio.getName()])}
        visitados_fim = {fim.getId(): (0, [fim.getName()])}

        while fronteira_inicio and fronteira_fim:
            # Expande a fronteira da parte do início
            caminho_inicio, custo_inicio = self.expandir_fronteira_custo_otimizado(
                fronteira_inicio, visitados_inicio, visitados_fim
            )
            if caminho_inicio:
                return caminho_inicio, custo_inicio

            # Expande a fronteira da parte do fim
            caminho_fim, custo_fim = self.expandir_fronteira_custo_otimizado(
                fronteira_fim, visitados_fim, visitados_inicio
            )
            if caminho_fim:
                return caminho_fim, custo_fim

        return None, float('inf')

    def expandir_fronteira_custo_otimizado(self, fronteira, visitados_atual, visitados_oposto):
        if not fronteira:
            return None, float('inf')

        # Retira o nó com menor custo acumulado
        custo_atual, no_atual, caminho = heapq.heappop(fronteira)

        # Expande os vizinhos do nó atual
        for vizinho_id, peso in self.get_neighbors(no_atual).items():
            novo_custo = custo_atual + peso

            # Verifica se o vizinho está na outra fronteira (interseção)
            if vizinho_id in visitados_oposto:
                custo_oposto, caminho_oposto = visitados_oposto[vizinho_id]
                caminho_combinado = caminho + caminho_oposto[::-1][1:]
                custo_total = novo_custo + custo_oposto
                return caminho_combinado, custo_total

            # Se o vizinho ainda não foi visitado ou se o novo custo for menor
            if vizinho_id not in visitados_atual or novo_custo < visitados_atual[vizinho_id][0]:
                vizinho = self.nodes[vizinho_id]['node']
                visitados_atual[vizinho_id] = (novo_custo, caminho + [vizinho.getName()])
                heapq.heappush(fronteira, (novo_custo, vizinho, caminho + [vizinho.getName()]))

        return None, float('inf')

    def busca_a_estrela(self, inicio_name, objetivo_name):
        inicio = self.find_node_by_name(inicio_name)
        objetivo = self.find_node_by_name(objetivo_name)

        if not inicio or not objetivo:
            print(f"Erro: Nós '{inicio_name}' ou '{objetivo_name}' não encontrados.")
            return None, float('inf')

        # Inicializações
        fila_prioridade = []
        heapq.heappush(fila_prioridade, (0 + inicio.getHeuristica(), inicio))  # (f(n), nó)
        custos = {inicio: 0}  # g(n): custo acumulado do início até o nó
        predecessores = {inicio: None}  # Para reconstruir o caminho

        while fila_prioridade:
            # Pega o nó com menor f(n)
            _, atual = heapq.heappop(fila_prioridade)

            # Se chegou ao objetivo, reconstrua o caminho
            if atual == objetivo:
                caminho = []
                while atual:
                    caminho.append(atual)
                    atual = predecessores[atual]
                caminho.reverse()
                # Converte o caminho para uma lista de nomes antes de retornar
                return [node.getName() for node in caminho], custos[objetivo]

            # Explorar os vizinhos do nó atual
            for vizinho_id, custo_aresta in self.get_neighbors(atual).items():
                # Usar `find_node_by_id` para buscar o vizinho pelo ID
                vizinho = self.find_node_by_id(vizinho_id)
                if vizinho is None:
                    print(f"Erro: Vizinho com ID '{vizinho_id}' não encontrado no grafo.")
                    continue

                # Calcular novo custo acumulado
                novo_custo = custos[atual] + custo_aresta

                # Atualizar custos e predecessores se encontrar um caminho melhor
                if vizinho not in custos or novo_custo < custos[vizinho]:
                    custos[vizinho] = novo_custo
                    predecessores[vizinho] = atual
                    f_n = novo_custo + vizinho.getHeuristica()
                    heapq.heappush(fila_prioridade, (f_n, vizinho))

        # Se não houver caminho para o objetivo
        return None, float('inf')

    def busca_gulosa(self, inicio_nome, objetivo_nome):
        inicio = self.find_node_by_name(inicio_nome)
        objetivo = self.find_node_by_name(objetivo_nome)

        if not inicio or not objetivo:
            print(f"Erro: Nó '{inicio_nome}' ou '{objetivo_nome}' não encontrado.")
            return None, 0

        fila_prioridade = [(inicio.getHeuristica(), inicio)]
        visitados = set()
        predecessores = {inicio.getId(): None}

        while fila_prioridade:
            # Seleciona o nó com menor heurística
            _, atual = heapq.heappop(fila_prioridade)

            # Verifica se chegou ao objetivo
            if atual == objetivo:
                caminho = []
                while atual:
                    caminho.append(atual.getName())
                    atual = self.find_node_by_id(predecessores[atual.getId()])
                caminho.reverse()

                custo = self.calculate_path_cost(caminho)
                return caminho, custo

            # Marca o nó como visitado
            visitados.add(atual.getId())

            # Explora os vizinhos
            for vizinho_id, peso in self.get_neighbors(atual).items():
                if vizinho_id not in visitados:
                    vizinho = self.find_node_by_id(vizinho_id)
                    if vizinho:
                        heapq.heappush(fila_prioridade, (vizinho.getHeuristica(), vizinho))
                        predecessores[vizinho.getId()] = atual.getId()

        print(f"Caminho não encontrado de '{inicio_nome}' para '{objetivo_nome}'.")
        return None, float('inf')

    def causar_terramoto_random(self):
        if not self.nodes:  # Verifica se há nós no grafo
            print("O grafo está vazio! Nenhum terremoto pode ser causado.")
            return

        # Seleciona um nó aleatório
        node_data = random.choice(list(self.nodes.values()))
        node = node_data['node']  # Extrai o objeto Node da entrada selecionada

        # Aumenta a heurística do nó
        nova_heuristica = node.getHeuristica() + 1000
        node.setHeuristica(nova_heuristica)

        print(f"Terremoto causado em {node.getName()}!")

    def causar_terramoto(self, node_name):

        node = self.find_node_by_name(node_name)

        if node is None:
            print(f"Nó '{node_name}' não encontrado. Nenhum terremoto pode ser causado.")
            return

        # Aumenta a heurística do nó
        nova_heuristica = node.getHeuristica() + 1000
        node.setHeuristica(nova_heuristica)

        print(f"Terremoto causado em {node.getName()}!")

    def listar_nos_por_prioridade(self):
        # Filtra os nós com prioridade maior que 0
        nos_filtrados = [data['node'] for data in self.nodes.values() if data['node'].getPriority() > 0]

        # Verifica se há nós com prioridade > 0
        if not nos_filtrados:
            return []

        # Ordena os nós filtrados por prioridade, em ordem decrescente
        nos_ordenados = sorted(nos_filtrados, key=lambda x: x.getPriority(), reverse=True)

        return nos_ordenados

    def entregar_por_prioridade(self, start_name, algoritmo):
        nos_ordenados = self.listar_nos_por_prioridade()

        if not nos_ordenados:
            print("Não há entregas a serem realizadas. Todos os nós possuem prioridade 0.")
            return [], 0
        caminho_completo = []
        custo_total = 0  # Para armazenar o custo total acumulado
        ultimo_no = None  # Para rastrear o último nó visitado

        # Dicionário para mapear algoritmos às funções correspondentes
        algoritmos = {
            1: self.busca_a_estrela,  # A*
            2: self.busca_gulosa,  # Greedy
            3: self.procura_DFS,  # DFS
            4: self.procura_BFS,  # BFS
            5: self.busca_bidirecional,  # Bidirecional
            6: self.busca_custo_uniforme  # Custo uniforme
        }

        # Verificar se o algoritmo selecionado existe
        if algoritmo not in algoritmos:
            print(f"Erro: Algoritmo {algoritmo} não é válido.")
            return [], 0

        busca_funcao = algoritmos[algoritmo]

        for node in nos_ordenados:
            if not ultimo_no:
                # Para o primeiro nó, calcula o custo de Lisboa até o primeiro nó
                caminho, custo = busca_funcao(start_name, node.getName())
            else:
                # Calcula custo do último nó visitado até o próximo nó
                caminho_ultimo, custo_ultimo = busca_funcao(ultimo_no.getName(), node.getName())
                # Calcula custo de Lisboa até o próximo nó
                caminho_lisboa, custo_lisboa = busca_funcao(start_name, node.getName())

                # Escolhe o menor custo
                if custo_ultimo < custo_lisboa:
                    caminho, custo = caminho_ultimo, custo_ultimo
                else:
                    caminho, custo = caminho_lisboa, custo_lisboa

            if caminho:
                # Evita duplicar o último nó no caminho
                if caminho_completo and caminho[0] == caminho_completo[-1]:
                    caminho = caminho[1:]
                caminho_completo.extend(caminho)
                custo_total += custo

                # Adiciona "Entrega realizada" quando chega ao nó de entrega
                caminho_completo.append("Entrega realizada")
            else:
                print(f"Erro: Caminho não encontrado para {node.getName()}.")

            # Atualiza o último nó visitado
            ultimo_no = node

        return caminho_completo, custo_total

    def filtrar_entregas_realizadas(self, lista):

        return [item for item in lista if item != "Entrega realizada"]

    def selecionar_veiculo_para_entrega(self, caminho):
        if isinstance(caminho, tuple):
            caminho, _ = caminho  # Desempacota o caminho, ignorando o segundo elemento do tuplo
        if not isinstance(caminho, list) or any(not isinstance(no, str) for no in caminho):
            print("Erro: Caminho deve ser uma lista de nomes de nós.")
            return None

        if not caminho:
            print("Erro: Caminho inválido.")
            return None

        primeiro_no = self.find_node_by_name(caminho[0])
        if not primeiro_no:
            print(f"Erro: O primeiro nó '{caminho[0]}' não foi encontrado.")
            return None

        # Acessibilidade inicial dos veículos no primeiro nó
        veiculos_acessiveis = set(primeiro_no.getAccessibility())  # Retorna objetos `Vehicle`

        # Soma os suprimentos necessários ao longo do caminho, ignorando nós repetidos consecutivos
        total_suprimentos = 0
        last_node_name = None
        for nome_no in caminho:
            if nome_no == last_node_name:  # Ignora nós consecutivos iguais
                continue
            last_node_name = nome_no

            no = self.find_node_by_name(nome_no)
            if no:
                total_suprimentos += no.getsuprimentosNecessarios()
                veiculos_acessiveis.intersection_update(no.getAccessibility())  # Filtra veículos acessíveis
                if not veiculos_acessiveis:
                    print(f"Nenhum veículo acessível a todos os nós do caminho.")
                    return None
            else:
                print(f"Erro: Nó '{nome_no}' não encontrado no grafo.")
                return None

        print(f"Soma total dos suprimentos necessários ao longo do caminho: {total_suprimentos} kg")

        # Ordena veículos por capacidade mínima suficiente (ordem crescente de capacidade)
        veiculos_ordenados = sorted(
            veiculos_acessiveis,
            key=lambda v: v.getCapacity()
        )

        # Seleciona o menor veículo com capacidade suficiente
        for veiculo in veiculos_ordenados:
            if veiculo.getCapacity() >= total_suprimentos:
                print(
                    f"Veículo selecionado: {veiculo.getName()} com capacidade {veiculo.getCapacity()} kg "
                    f"e velocidade {veiculo.getSpeed()} km/h."
                )
                return veiculo

        # Se nenhum veículo tiver capacidade suficiente, calcula quantos veículos iguais seriam necessários
        maior_veiculo = max(veiculos_ordenados, key=lambda v: v.getCapacity())
        capacidade_veiculo = maior_veiculo.getCapacity()
        num_veiculos = -(-total_suprimentos // capacidade_veiculo)  # Arredonda para cima

        print(
            f"Veículo selecionado: {maior_veiculo.getName()} com capacidade {capacidade_veiculo} kg "
            f"e velocidade {maior_veiculo.getSpeed()} km/h.\n"
            f"Número de veículos necessários (simultaneamente): {num_veiculos}."
        )
        return maior_veiculo

    def formatar_tempo(self, total_horas):

        horas = int(total_horas)  # Parte inteira das horas
        minutos = int((total_horas - horas) * 60)  # Parte decimal convertida para minutos
        return f"{horas} horas e {minutos} minutos"

    def verify_deadline_with_path(self, path, vehicle_name, current_time=0):
        if not path or len(path) < 2:
            print("Erro: O caminho deve ter pelo menos dois nós.")
            return None, False, current_time

        total_time = current_time
        total_cost = 0

        for i in range(len(path) - 1):
            start_node_name = path[i]
            end_node_name = path[i + 1]

            if start_node_name == end_node_name:  # Ignora nós consecutivos iguais
                current_time+=20
                print("Entrega realizada.Adicionados 20 minutos.")
                continue

            if end_node_name == "Lisboa":
                # Ignora a "aresta" fictícia que retorna a Lisboa
                print(f"Veículo retornou à base em Lisboa. Ignorando aresta '{start_node_name} -> Lisboa'.")
                continue

            start_node = self.find_node_by_name(start_node_name)
            end_node = self.find_node_by_name(end_node_name)

            if not start_node or not end_node:
                print(f"Erro: Nós '{start_node_name}' ou '{end_node_name}' não encontrados.")
                return None, False, total_time

            vehicle = end_node.get_vehicle_by_name(vehicle_name)
            if not vehicle:
                print(f"Erro: Veículo '{vehicle_name}' não encontrado no nó '{end_node.getName()}'.")
                return None, False, total_time

            # Reabastecer o veículo antes de começar o trajeto
            vehicle.refuel(100 - vehicle.getFuel())

            # Obter o peso e ajustar a velocidade com base nele
            vehicle_weight = vehicle.getPeso()
            carga_ratio = total_cost / vehicle.getCapacity()
            carga_ratio = min(1.0, carga_ratio)
            adjusted_speed_base = vehicle.getSpeed() * (1 - 0.3 * carga_ratio)

            # Fator de ajuste pela relação entre peso e desempenho
            weight_penalty_factor = max(0.5, 1 - (vehicle_weight / 10000))  # Penalizamos veículos >10,000kg
            adjusted_speed_base *= weight_penalty_factor

            # Obter o custo da aresta
            edge_cost = self.nodes[start_node.getId()]['edges'].get(end_node.getId())
            if edge_cost is None:
                print(f"Erro: Não há aresta entre os nós '{start_node.getName()}' e '{end_node.getName()}'.")
                return None, False, total_time

            weather_impact = self.getWeatherImpact(end_node)
            if weather_impact == 0:
                print(f"Erro: O nó '{end_node.getName()}' está inacessível devido a um desastre ambiental.")
                return None, False, total_time

            # Velocidade ajustada com base no impacto do clima
            adjusted_speed = adjusted_speed_base * weather_impact

            # Cálculo do tempo ajustado para a aresta
            time_for_edge = edge_cost / adjusted_speed
            total_time += time_for_edge
            total_cost += edge_cost

            # Diminuir o combustível do veículo com base na distância percorrida
            vehicle.decreaseFuel(edge_cost)

            # Verificar se o veículo ainda tem combustível para continuar
            if vehicle.getFuel() <= 0:
                print(f"Erro: Veículo '{vehicle_name}' ficou sem combustível no trajeto.")
                return None, False, total_time
            t = self.formatar_tempo(total_time)
            # Verificar a deadline do nó atual (entrega é realizada aqui)
            delivery_deadline = end_node.getDeliveryDeadline()
            if delivery_deadline is not None and total_time > delivery_deadline:
                print(
                    f"Erro: Entrega no nó '{end_node.getName()}' excedeu a deadline. Tempo: {t}, Deadline: {delivery_deadline:.2f} horas.")
                return total_time, False, total_time

        print(
            f"Entrega realizada em {t}")
        return total_time, True, total_time

    def compare_algorithms(self, start_name, end_name):
        # Localizar os nós de início e fim
        start = self.find_node_by_name(start_name)
        end = self.find_node_by_name(end_name)

        if not start or not end:
            print(f"Erro: Nó(s) '{start_name}' ou '{end_name}' não encontrado(s) no grafo.")
            return

        results = []

        # Executar todos os algoritmos e armazenar os resultados
        caminho, custo = self.procura_BFS(start_name, end_name)
        custo = custo if custo is not None else float('inf')
        results.append(("BFS", custo))

        caminho, custo = self.procura_DFS(start_name, end_name)
        custo = custo if custo is not None else float('inf')
        results.append(("DFS", custo))

        caminho, custo = self.busca_custo_uniforme(start_name, end_name)
        custo = custo if custo is not None else float('inf')
        results.append(("Custo Uniforme", custo))

        caminho, custo = self.busca_bidirecional(start_name, end_name)
        custo = custo if custo is not None else float('inf')
        results.append(("Bidirecional", custo))

        caminho, custo = self.busca_a_estrela(start_name, end_name)
        custo = custo if custo is not None else float('inf')
        results.append(("A*", custo))

        caminho, custo = self.busca_gulosa(start_name, end_name)
        custo = custo if custo is not None else float('inf')
        results.append(("Gulosa", custo))

        # Ordenar os resultados por custo
        results.sort(key=lambda x: x[1])

        # Exibir os resultados
        print("\n--- Comparação de Algoritmos por Kms---")
        for alg, cost in results:
            if cost != float('inf'):
                print(f"{alg}: {cost} kms")
            else:
                print(f"{alg}: Caminho não encontrado")

    def dividir_entregas(self, caminho, entrega="Entrega realizada", base="Lisboa"):
        subcaminhos = []
        subcaminho_atual = []

        for nodo in caminho:
            subcaminho_atual.append(nodo)

            # Caso 1: Encontrou "Entrega realizada"
            if nodo == entrega:
                subcaminhos.append(subcaminho_atual[:-1])  # Adiciona o subcaminho sem "Entrega realizada"
                subcaminho_atual = []  # Reinicia o subcaminho

            # Caso 2: Retorno à base
            elif nodo == base and len(subcaminho_atual) > 1:
                subcaminhos.append(subcaminho_atual[:-1])  # Adiciona o subcaminho antes da base
                subcaminho_atual = [base]  # Reinicia o subcaminho partindo da base

        # Adiciona o último subcaminho, se ainda houver nós restantes
        if subcaminho_atual:
            subcaminhos.append(subcaminho_atual)

        return subcaminhos

    def dividir_caminho(self, caminho, entrega="Entrega realizada", base="Lisboa"):
        subcaminhos = []
        subcaminho_atual = []

        for nodo in caminho:
            subcaminho_atual.append(nodo)

            # Caso 1: Encontrou "Entrega realizada"
            if nodo == entrega:
                subcaminhos.append(subcaminho_atual[:-1])  # Adiciona o subcaminho sem "Entrega realizada"
                subcaminho_atual = []  # Reinicia o subcaminho

            # Caso 2: Retorno à base
            elif nodo == base and len(subcaminho_atual) > 1:
                subcaminhos.append(subcaminho_atual[:-1])  # Adiciona o subcaminho antes da base
                subcaminho_atual = [base]  # Reinicia o subcaminho partindo da base

        # Adiciona o último subcaminho, se ainda houver nós restantes
        if subcaminho_atual:
            subcaminhos.append(subcaminho_atual)

        # Combinar subcaminhos consecutivos que não começam em "Lisboa"
        subcaminhos_combinados = []
        for subcaminho in subcaminhos:
            if not subcaminhos_combinados or subcaminho[0] == base:
                subcaminhos_combinados.append(subcaminho)  # Adiciona um novo subcaminho
            else:
                subcaminhos_combinados[-1].extend(subcaminho)  # Combina com o subcaminho anterior

        return subcaminhos_combinados

    def atualizar_prioridade_e_suprimentos(self, node_name, prioridade, suprimentos):
        node = self.find_node_by_name(node_name)  # Localiza o nó pelo nome
        if node:
            # Verifica se os suprimentos necessários são diferentes de 0
            if node.getsuprimentosNecessarios() != 0:
                node.setPriority(prioridade)  # Atualiza a prioridade do nó
                node.setsuprimentosNecessarios(suprimentos)  # Atualiza os suprimentos necessários do nó
                print(f"Nó '{node.getName()}' atualizado: Prioridade={prioridade}, Suprimentos={suprimentos}.")
        else:
            print(f"Erro")

    def __str__(self):
        result = ""
        for node_id, node_data in self.nodes.items():
            node_name = node_data['node'].getName()  # Assume-se que o método getName() está implementado na classe Node
            edges = node_data['edges']
            edges_str = ", ".join(
                [f"({self.nodes[dest_id]['node'].getName()} - {weight})" for dest_id, weight in edges.items()])
            result += f"{node_name}: {edges_str}\n"
        return result

    def __repr__(self):
        return self.__str__()
