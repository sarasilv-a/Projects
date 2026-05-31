from carregar_dados_portugal import carregar_dados_portugal
from colorama import Fore, Style


def display_menuPrincipal():
    print("\n--- Bem vindo ---")
    print("1. Resolver com Algoritmos de Pesquisa Informada!")
    print("2. Resolver com Algoritmos de Pesquisa Não Informada!")
    print("3. Resolver com Algoritmo Criado para Solução do Problema!")
    print("4. Desenhar Grafo!")
    print("5. Causar Desastre Ambiental!")
    print("6. Comparar de algoritmos em termos de distância!")
    print("7. Recarregar Dados!")
    print("8. Sair!")


def display_menui():
    print("\n--- Menu Pesquisa Informada ---")
    print("1. Busca A*")
    print("2. Busca Greedy")


def display_menun():
    print("\n--- Menu Pesquisa Não Informada ---")
    print("1. Executar BFS")
    print("2. Executar DFS")
    print("3. Custo Uniforme")
    print("4. Bidirecional")


def display_menuDesastre():
    print("\n--- Menu Desastre ---")
    print("1. Executar Desastre em concelho Aleatório!")
    print("2. Executar Desastre em concelho Específico!")


def carregar_grafo():
    while True:
        print("\n--- Escolha o número de entregas ---")
        print("1. Uma entrega")
        print("2. Duas entregas")
        print("3. Três entregas")

        entrega_choice = input("Escolha uma opção (1, 2 ou 3): ")

        if entrega_choice == '1':
            grafo_file = "1_entrega.json"
            break
        elif entrega_choice == '3':
            grafo_file = "3_entregas.json"
            break
        elif entrega_choice == '2':
            grafo_file = "portugal.json"
            break
        else:
            print("Opção inválida. Tente novamente.")

    graph, vehicles = carregar_dados_portugal(grafo_file)

    if not graph or not vehicles:
        print("Erro ao carregar o grafo ou os veículos. Verifique os dados.")
        return None, None

    return graph, vehicles


def main():
    graph, vehicles = carregar_grafo()
    if not graph:
        print(f"{Fore.RED}Encerrando programa devido a erro no carregamento.{Style.RESET_ALL}")
        return

    while True:
        display_menuPrincipal()
        choice = input("Escolha uma opção: ")

        if choice == '1':  # Pesquisa Informada
            display_menui()
            choice1 = input("Escolha uma opção: ")

            if choice1 == '1':  # Busca A*
                start = input("Digite o nome do concelho inicial: ")
                end = input("Digite o nome do concelho final: ")
                caminho, custo = graph.busca_a_estrela(start, end)
                veiculo = graph.selecionar_veiculo_para_entrega(caminho)
                print(f"{Fore.GREEN}Caminho encontrado:{Style.RESET_ALL} {caminho}")
                print(f"{Fore.CYAN}Veículo selecionado:{Style.RESET_ALL} {veiculo}")
                print(f"{Fore.YELLOW}Custo total:{Style.RESET_ALL} {custo} km.")

            elif choice1 == '2':  # Busca Greedy
                start = input("Digite o nome do concelho inicial: ")
                end = input("Digite o nome do concelho final: ")
                caminho, custo = graph.busca_gulosa(start, end)
                veiculo = graph.selecionar_veiculo_para_entrega(caminho)
                print(f"{Fore.GREEN}Caminho encontrado:{Style.RESET_ALL} {caminho}")
                print(f"{Fore.CYAN}Veículo selecionado:{Style.RESET_ALL} {veiculo}")
                print(f"{Fore.YELLOW}Custo total:{Style.RESET_ALL} {custo} km.")

            else:
                print(f"{Fore.RED}Opção inválida no menu de Pesquisa Informada.{Style.RESET_ALL}")

        elif choice == '2':  # Pesquisa Não Informada
            display_menun()
            choice2 = input("Escolha uma opção: ")

            if choice2 == '1':  # BFS
                start = input("Digite o nome do concelho inicial: ")
                end = input("Digite o nome do concelho final: ")
                caminho, custo = graph.procura_BFS(start, end)
                veiculo = graph.selecionar_veiculo_para_entrega(caminho)
                print(f"{Fore.GREEN}Caminho encontrado:{Style.RESET_ALL} {caminho}")
                print(f"{Fore.CYAN}Veículo selecionado:{Style.RESET_ALL} {veiculo}")
                print(f"{Fore.YELLOW}Custo total:{Style.RESET_ALL} {custo} km.")

            elif choice2 == '2':  # DFS
                start = input("Digite o nome do concelho inicial: ")
                end = input("Digite o nome do concelho final: ")
                caminho, custo = graph.procura_DFS(start, end)
                veiculo = graph.selecionar_veiculo_para_entrega(caminho)
                print(f"{Fore.GREEN}Caminho encontrado:{Style.RESET_ALL} {caminho}")
                print(f"{Fore.CYAN}Veículo selecionado:{Style.RESET_ALL} {veiculo}")
                print(f"{Fore.YELLOW}Custo total:{Style.RESET_ALL} {custo} km.")

            elif choice2 == '3':  # Custo Uniforme
                start = input("Digite o nome do concelho inicial: ")
                end = input("Digite o nome do concelho final: ")
                caminho, custo = graph.busca_custo_uniforme(start, end)
                veiculo = graph.selecionar_veiculo_para_entrega(caminho)
                print(f"{Fore.GREEN}Caminho encontrado:{Style.RESET_ALL} {caminho}")
                print(f"{Fore.CYAN}Veículo selecionado:{Style.RESET_ALL} {veiculo}")
                print(f"{Fore.YELLOW}Custo total:{Style.RESET_ALL} {custo} km.")

            elif choice2 == '4':  # Bidirecional
                start = input("Digite o nome do concelho inicial: ")
                end = input("Digite o nome do concelho final: ")
                caminho, custo = graph.busca_bidirecional(start, end)
                veiculo = graph.selecionar_veiculo_para_entrega(caminho)
                print(f"{Fore.GREEN}Caminho encontrado:{Style.RESET_ALL} {caminho}")
                print(f"{Fore.CYAN}Veículo selecionado:{Style.RESET_ALL} {veiculo}")
                print(f"{Fore.YELLOW}Custo total:{Style.RESET_ALL} {custo} km.")

            else:
                print(f"{Fore.RED}Opção inválida no menu de Pesquisa Não Informada.{Style.RESET_ALL}")


        elif choice == '3':
            alg = int(input(

                "Escolha o algoritmo a ser usado para as entregas:\n"

                "1 - A* (Busca A-estrela)\n"

                "2 - Greedy (Busca Gulosa)\n"

                "3 - DFS (Busca em Profundidade)\n"

                "4 - BFS (Busca em Largura)\n"

                "5 - Bidirecional\n"

                "6 - Custo Uniforme\n"

                "Digite o número correspondente ao algoritmo: "

            ))
            caminho, custo = graph.entregar_por_prioridade("Lisboa", alg)

            entregas = graph.dividir_entregas(caminho)

            print(f"{Fore.GREEN}Entregas divididas:{Style.RESET_ALL}")

            for i, sub in enumerate(entregas):
                print(f"{Fore.CYAN}Entrega {i + 1}:{Style.RESET_ALL} {sub}")

            subcaminhos = graph.dividir_caminho(caminho)

            current_time = 0
            total_custo = 0

            for i, subcaminho in enumerate(subcaminhos):
                print(f"\n{Fore.YELLOW}Subcaminho {i + 1}:{Style.RESET_ALL} {subcaminho}")

                veiculo = graph.selecionar_veiculo_para_entrega(subcaminho)
                if veiculo is None:
                    print(
                        f"{Fore.RED}Erro: Nenhum veículo disponível para esta entrega. Subcaminho ignorado.{Style.RESET_ALL}")
                    continue

                vehicle_name = veiculo.getName() if hasattr(veiculo, 'getName') else veiculo
                if subcaminho[0] == "Lisboa":
                    current_time = 0
                total_time, sucesso, current_time = graph.verify_deadline_with_path(subcaminho, vehicle_name,
                                                                                    current_time)

                if sucesso:
                    print(f"{Fore.GREEN}Subcaminho {i + 1} concluído com sucesso dentro da deadline.{Style.RESET_ALL}")

                    for node in subcaminho:
                        graph.atualizar_prioridade_e_suprimentos(node,0, 0)
                else:
                    print(f"{Fore.RED}Subcaminho {i + 1} falhou. Deadline ultrapassada.{Style.RESET_ALL}")

                # Acumular o custo do subcaminho
                total_custo += custo

            print(f"\n{Fore.GREEN}Caminho completo processado.{Style.RESET_ALL} "
                  f"{Fore.YELLOW}Custo total:{Style.RESET_ALL} {total_custo} km.")

        elif choice == '4':  # Desenhar Grafo
            print(f"{Fore.CYAN}Desenhando o Grafo...{Style.RESET_ALL}")
            graph.desenha()

        elif choice == '5':  # Causar Desastre Ambiental
            display_menuDesastre()
            choice3 = input("Escolha uma opção: ")
            if choice3 == '1':
                graph.causar_terramoto_random()
                print(f"{Fore.RED}Desastre aleatório causado.{Style.RESET_ALL}")
            elif choice3 == '2':
                nodo = input("Digite o nome do concelho que quer causar o terramoto: ")
                graph.causar_terramoto(nodo)
                print(f"{Fore.RED}Desastre causado no concelho: {nodo}.{Style.RESET_ALL}")

        elif choice == '6':  # Comparar algoritmos
            start = input("Digite o nome do concelho inicial: ")
            end = input("Digite o nome do concelho final: ")
            graph.compare_algorithms(start, end)
            print(f"{Fore.YELLOW}Comparação de algoritmos concluída.{Style.RESET_ALL}")

        elif choice == '7':  # Recarregar Dados
            graph, vehicles = carregar_grafo()
            if not graph:
                print(f"{Fore.RED}Erro ao recarregar os dados. Mantendo a configuração atual.{Style.RESET_ALL}")
            else:
                print(f"{Fore.GREEN}Dados recarregados com sucesso.{Style.RESET_ALL}")


        elif choice == '8':  # Sair
            print(f"{Fore.CYAN}Saindo...{Style.RESET_ALL}")
            break

        else:
            print(f"{Fore.RED}Opção inválida. Tente novamente.{Style.RESET_ALL}")


if __name__ == "__main__":
    main()
