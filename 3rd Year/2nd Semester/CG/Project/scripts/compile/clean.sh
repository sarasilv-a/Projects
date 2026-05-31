#!/bin/bash

echo "Limpando arquivos de compilação..."

# Limpar arquivos da build (se existir)
if [[ -d "build" ]]; then
    echo "Removendo arquivos em 'build/'..."
    cd build && make clean && cd ..
fi

# Remover modelos gerados (se existirem)
if [[ -d "src/models" ]]; then
    echo "Removendo modelos em 'src/models/'..."
    rm -f src/models/*.3d
fi

echo "Limpeza concluída!"
