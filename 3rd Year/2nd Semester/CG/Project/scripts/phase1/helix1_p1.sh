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


# Gerar o modelo
echo "Gerando modelo..."
cd "$BUILD_DIR" && ./generator helix 2 5 10 30 helix_2_5_10_30.3d && cd -

# Verificar se o modelo foi gerado
if [[ ! -f "$MODELS/helix_2_5_10_30.3d" ]]; then
    echo "Erro: modelo não gerado. Verifique permissões e caminhos."
    exit 1
fi

# Executar o engine
echo "Executando engine..."
cd "$BUILD_DIR" && ./engine "../$SCENES/ours_tests/test_1_helix1.xml"