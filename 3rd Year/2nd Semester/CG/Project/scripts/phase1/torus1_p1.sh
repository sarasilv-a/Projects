#!/bin/bash

BUILD_DIR="build"
GENERATOR="$BUILD_DIR/generator"
ENGINE="$BUILD_DIR/engine"
MODELS="src/models"
SCENES="src/scenes"

# Compilar se necessário
if [[ ! -f "$GENERATOR" || ! -f "$ENGINE" ]]; then
    echo "Compilando projeto..."
    ./scripts/compile/build.sh
fi


# Gerar o modelo
echo "Gerando modelo..."
cd "$BUILD_DIR" && ./generator torus 3 1 20 15 torus_3_1_20_15.3d && cd -

# Verificar se o modelo foi gerado
if [[ ! -f "$MODELS/torus_3_1_20_15.3d" ]]; then
    echo "Erro: modelo não gerado. Verifique permissões e caminhos."
    exit 1
fi

# Executar o engine
echo "Executando engine..."
cd "$BUILD_DIR" && ./engine "../$SCENES/ours_tests/test_1_torus1.xml"