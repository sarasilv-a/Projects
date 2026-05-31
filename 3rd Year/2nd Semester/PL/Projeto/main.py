import sys
from parser import parser, reset_parser
from contextlib import redirect_stdout

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python main.py <caminho_para_ficheiro_pascal>")
        sys.exit(1)

    caminho_ficheiro = sys.argv[1]

    try:
        with open(caminho_ficheiro, "r", encoding="utf-8") as f:
            codigo = f.read()

        with open("ewvm_output.txt", "w", encoding="utf-8") as out:
            with redirect_stdout(out):
                reset_parser(parser)
                parser.parse(codigo)

        print(f"Código gerado com sucesso! Output guardado em 'ewvm_output.txt'.")

    except FileNotFoundError:
        print(f"Erro: ficheiro '{caminho_ficheiro}' não encontrado.")
