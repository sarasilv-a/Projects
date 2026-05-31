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

cd "$BUILD_DIR" || exit 1

# Gerar sistema solar
./generator solar

# Engine
echo "Executando engine para o sistema solar..."
./engine "../$SCENES/ours_tests/solar_system.xml"
cd - || exit 1

echo "Teste do sistema solar finalizado com sucesso!"