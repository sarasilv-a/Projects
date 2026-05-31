import os
import sys

print("Diretoria inicial:", os.getcwd())

# 1 — subir até raiz do projeto (exemplo: 3 níveis)
os.chdir(os.path.abspath(os.path.join(os.getcwd(), "../../..")))
print("Depois de subir 3 níveis:", os.getcwd())

# 2 — ir para o repositório que queres
target_path = "/home/core/Desktop/ESR/src"
os.chdir(target_path)
print("Diretoria final:", os.getcwd())

# 3 — definir PYTHONPATH
os.environ["PYTHONPATH"] = target_path
sys.path.append(target_path)

print("PYTHONPATH definido para:", os.environ["PYTHONPATH"])

