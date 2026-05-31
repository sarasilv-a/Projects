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

# Gerar o modelo necessário
echo "Gerando modelo..."
cd "$BUILD_DIR" && ./generator box 2 3 box_2_3.3d

# Verificar se o modelo foi gerado
if [[ ! -f "../$MODELS/box_2_3.3d" ]]; then
    echo "Erro: modelo não gerado. Verifique permissões e caminhos."
    exit 1
fi

# Executar o engine com o test_2_4.xml
echo "Executando engine para test_2_4.xml..."
./engine "../$SCENES/tests/test_files_phase_2/test_2_4.xml"
cd - || exit 1

echo "Teste 2_4 finalizado com sucesso!"
