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

# Função para gerar e verificar modelo
generate_model() {
    local shape=$1
    local params=$2
    local filename=$3

    echo "Gerando modelo: $filename ..."
    ./generator $shape $params $filename

    if [[ ! -f "../$MODELS/$filename" ]]; then
        echo "Erro: modelo não gerado. Verifique permissões e caminhos."
        exit 1
    fi
}

# Gerar modelos
generate_model "box" "2 3" "box_2_3.3d"
generate_model "cone" "1 2 4 3" "cone_1_2_4_3.3d"
generate_model "sphere" "1 8 8" "sphere_1_8_8.3d"

# Executar o engine
echo "Executando engine para test_2_2.xml..."
./engine "../$SCENES/tests/test_files_phase_2/test_2_2.xml"

cd - || exit 1

echo "Teste 2_2 finalizado com sucesso!"
