#!/bin/bash


# Compilar o projeto
echo "Compilando o projeto..."
cd build && make

# Verificar se os executáveis foram gerados
if [[ -f "generator" && -f "engine" ]]; then
    echo "Compilação concluída com sucesso!"
else
    echo "Erro na compilação!"
    exit 1
fi
