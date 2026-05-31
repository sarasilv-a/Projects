cmake_minimum_required(VERSION 3.10)
project(CG)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED True)

# Define o diretório de build
set(CMAKE_BINARY_DIR ${CMAKE_SOURCE_DIR}/build)
set(EXECUTABLE_OUTPUT_PATH ${CMAKE_BINARY_DIR})
set(LIBRARY_OUTPUT_PATH ${CMAKE_BINARY_DIR})

# Adiciona a pasta src/ para gerir os subprojetos
add_subdirectory(src)

# Verifica se estamos no Windows para configurar o GLUT
if(WIN32)
    set(TOOLKITS_FOLDER "${CMAKE_SOURCE_DIR}/toolkits")

    if(NOT EXISTS "${TOOLKITS_FOLDER}/glut/GL/glut.h" OR NOT EXISTS "${TOOLKITS_FOLDER}/glut/glut32.lib")
        message(FATAL_ERROR "GLUT not found in toolkits folder!")
    endif()

    include_directories(${TOOLKITS_FOLDER}/glut)
    link_directories(${TOOLKITS_FOLDER}/glut)
endif()

file(COPY ${CMAKE_SOURCE_DIR}/textures DESTINATION ${CMAKE_BINARY_DIR})
file(COPY ${CMAKE_SOURCE_DIR}/textures DESTINATION ${CMAKE_BINARY_DIR}/Release)