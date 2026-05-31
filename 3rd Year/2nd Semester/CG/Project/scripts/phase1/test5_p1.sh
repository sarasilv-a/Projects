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
cd "$BUILD_DIR" && ./generator plane 2 3 plane_2_3.3d && cd -

# Verificar se o modelo foi gerado corretamente
if [[ ! -f "$MODELS/plane_2_3.3d" ]]; then
    echo "Erro: modelo não gerado. Verifique permissões e caminhos."
    exit 1
fi

cd "$BUILD_DIR" && ./generator sphere 1 10 10 sphere_1_10_10.3d && cd -

# Verificar se o modelo foi gerado 
if [[ ! -f "$MODELS/sphere_1_10_10.3d" ]]; then
    echo "Erro: modelo não gerado. Verifique permissões e caminhos."
    exit 1
fi

# Executar o engine
echo "Executando engine..."
cd "$BUILD_DIR" && ./engine "../$SCENES/tests/test_files_phase_1/test_1_5.xml"