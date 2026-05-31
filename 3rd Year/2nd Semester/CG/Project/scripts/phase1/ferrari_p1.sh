#!/bin/bash

BUILD_DIR="build"
GENERATOR="$BUILD_DIR/generator"
ENGINE="$BUILD_DIR/engine"
MODELS="src/models"
SCENES="src/scenes"

# Compilar
if [[ ! -f "$GENERATOR" || ! -f "$ENGINE" ]]; then
    echo "Compilando projeto..."
    ./scripts/compile/build.sh
fi

# Verificar se o modelo foi gerado
if [[ ! -f "$MODELS/ferrari.obj" ]]; then
    echo "Erro: modelo não gerado. Verifique permissões e caminhos."
    exit 1
fi

# Executar o engine
echo "Executando engine..."
cd "$BUILD_DIR" && ./engine "../$SCENES/ours_tests/ferrari.xml"