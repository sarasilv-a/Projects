cmake_minimum_required(VERSION 3.10)

# Nome do projeto
project(engine)

# Incluir todos os ficheiros .cpp automaticamente
file(GLOB SRC_FILES src/*.cpp)
include_directories(${CMAKE_SOURCE_DIR}/libs/rapidxml)
add_executable(${PROJECT_NAME} ${SRC_FILES})

# Incluir diretórios de headers
include_directories(${PROJECT_NAME} PUBLIC include)
target_link_libraries(${PROJECT_NAME} shared)

# Encontrar OpenGL
find_package(OpenGL REQUIRED)
include_directories(${OPENGL_INCLUDE_DIRS})
link_directories(${OPENGL_LIBRARY_DIRS})
add_definitions(${OPENGL_DEFINITIONS})

if(NOT OPENGL_FOUND)
    message(FATAL_ERROR "OpenGL not found!")
endif()

# Configuração para Windows
if(WIN32)
    message(STATUS "Configurando GLUT a partir da pasta 'toolkits'")
    message(STATUS "Toolkits_DIR set to: " ${TOOLKITS_FOLDER})
	set(TOOLKITS_FOLDER "" CACHE PATH "Path to Toolkits folder")

    # Caminho para a pasta dos toolkits
    set(TOOLKITS_FOLDER "${CMAKE_SOURCE_DIR}/toolkits")

    # Verificar se os ficheiros existem
    if(NOT EXISTS "${TOOLKITS_FOLDER}/glut/GL/glut.h" OR NOT EXISTS "${TOOLKITS_FOLDER}/glut/glut32.lib")
        message(FATAL_ERROR "GLUT not found in toolkits folder! Verifica se tens a versão correta (x32).")
    endif()
    if (NOT EXISTS "${TOOLKITS_FOLDER}/glew/GL/glew.h" OR NOT EXISTS "${TOOLKITS_FOLDER}/glew/glew32.lib")
        message(ERROR ": GLEW not found")
    endif (NOT EXISTS "${TOOLKITS_FOLDER}/glew/GL/glew.h" OR NOT EXISTS "${TOOLKITS_FOLDER}/glew/glew32.lib")	
    if (NOT EXISTS "${TOOLKITS_FOLDER}/devil/IL/il.h" OR NOT EXISTS "${TOOLKITS_FOLDER}/devil/devIL.lib")
		message(ERROR ": DevIL not found")
	endif (NOT EXISTS "${TOOLKITS_FOLDER}/devil/IL/il.h" OR NOT EXISTS "${TOOLKITS_FOLDER}/devil/devIL.lib")	
	

    # Incluir diretórios do GLUT e GLEW e DevIL
    include_directories(${TOOLKITS_FOLDER}/glut ${TOOLKITS_FOLDER}/glew ${TOOLKITS_FOLDER}/devil)
    link_directories(${TOOLKITS_FOLDER}/glut ${TOOLKITS_FOLDER}/glew ${TOOLKITS_FOLDER}/devil)

    # Ligar bibliotecas GLUT GLEW Devil e OpenGL
	target_link_libraries(${PROJECT_NAME} ${OPENGL_LIBRARIES} 
										  ${TOOLKITS_FOLDER}/glut/glut32.lib 
                                          ${TOOLKITS_FOLDER}/devil/devIL.lib
										  ${TOOLKITS_FOLDER}/glew/glew32.lib )

	if (EXISTS "${TOOLKITS_FOLDER}/glut/glut32.dll" AND EXISTS "${TOOLKITS_FOLDER}/glew/glew32.dll"
													AND EXISTS "${TOOLKITS_FOLDER}/devil/devil.dll")
		file(COPY ${TOOLKITS_FOLDER}/glut/glut32.dll DESTINATION ${CMAKE_BINARY_DIR})
		file(COPY ${TOOLKITS_FOLDER}/devil/devil.dll DESTINATION ${CMAKE_BINARY_DIR})
		file(COPY ${TOOLKITS_FOLDER}/glew/glew32.dll DESTINATION ${CMAKE_BINARY_DIR})
	endif(EXISTS "${TOOLKITS_FOLDER}/glut/glut32.dll" AND EXISTS "${TOOLKITS_FOLDER}/glew/glew32.dll"
													AND EXISTS "${TOOLKITS_FOLDER}/devil/devil.dll")

    set_property(DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR} PROPERTY VS_STARTUP_PROJECT ${PROJECT_NAME})

# Configuração para Linux e macOS
else (WIN32) #Linux and Mac

	set( CMAKE_CXX_FLAGS  "${CMAKE_CXX_FLAGS} Wno-deprecated")
	find_package(GLUT REQUIRED)
	include_directories(${GLUT_INCLUDE_DIR})
	link_directories(${GLUT_LIBRARY_DIRS})
	add_definitions(${GLUT_DEFINITIONS})
	
	if (NOT APPLE)
		find_package(GLEW REQUIRED)
		include_directories(${GLEW_INCLUDE_DIRS})
		link_libraries(${GLEW_LIBRARIES})
	endif(NOT APPLE)
	
	find_package(DevIL REQUIRED)
	link_libraries(${IL_LIBRARIES} )
	include_directories(${IL_INCLUDE_DIR})

	target_link_libraries(${PROJECT_NAME} ${OPENGL_LIBRARIES} ${GLUT_LIBRARIES} ${GLEW_LIBRARIES} ${IL_LIBRARIES})
	if(NOT GLUT_FOUND)
	   message(ERROR ": GLUT not found!")
	endif(NOT GLUT_FOUND)
	
endif(WIN32)

