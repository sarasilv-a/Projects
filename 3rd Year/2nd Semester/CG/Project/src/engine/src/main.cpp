#define _USE_MATH_DEFINES
#include <math.h>
#include <vector>
#include <string>
#include <iostream>

#include "parse.hpp"
#include "catmull_curve.hpp"
#include "../../shared/include/fileUtils.hpp"

#include <IL/il.h>

#ifdef __APPLE__
#include <GLUT/glut.h>
#else
#include <GL/glew.h>
#include <GL/glut.h>
#endif

#define MODELS "../src/models/"

// variáveis da câmera
float camRadius, camHorizontal, camElevation;

bool axis = true; // eixos ativos ou não

bool light = false; // luz ativa ou não
bool catmull = true; // ativar catmull ou não
bool normals = false; // ativar normais ou não

int drawMode = GL_FILL; // modo de desenho

float fps = 0.0f; // frames por segundo
int frame = 0;
int timebase = 0;

Configuration config;


void frameCounter() {
    frame++;
    int currentTime = glutGet(GLUT_ELAPSED_TIME);

    if (currentTime - timebase > 1000) {
        fps = frame * 1000.0f / (currentTime - timebase);
        timebase = currentTime;
        frame = 0;

        char title[32];
        sprintf_s(title, "CG Engine - FPS: %.2f", fps);
        glutSetWindowTitle(title);
    }
}

// Função para redimensionar
void reshape(int w, int h) {
    float aspect_ratio = (float)w / (float)h;
    glViewport(0, 0, w, h);

    glMatrixMode(GL_PROJECTION);
    glLoadIdentity();
    gluPerspective(config.camera.fov, aspect_ratio, config.camera.near, config.camera.far);
    
    glMatrixMode(GL_MODELVIEW);
}

// Função para desenhar os eixos x y z
void drawAxis() {
    if (axis) {
        glDisable(GL_LIGHTING);

        glBegin(GL_LINES);
        glColor3f(1.0f, 0.0f, 0.0f); // X (vermelho)
        glVertex3f(-500.0f, 0.0f, 0.0f);
        glVertex3f(500.0f, 0.0f, 0.0f);
        glColor3f(0.0f, 1.0f, 0.0f); // Y (verde)
        glVertex3f(0.0f, -500.0f, 0.0f);
        glVertex3f(0.0f, 500.0f, 0.0f);
        glColor3f(0.0f, 0.0f, 1.0f); // Z (azul)
        glVertex3f(0.0f, 0.0f, -500.0f);
        glVertex3f(0.0f, 0.0f, 500.0f);
        glEnd();

        if (light) {
            glEnable(GL_LIGHTING);
        }
    }
}

// Inicializar câmara
void initCamera() {
    float x = config.camera.position.x;
    float y = config.camera.position.y;
    float z = config.camera.position.z;

    camRadius = sqrt(x*x + y*y + z*z); 
    camHorizontal = atan2(x, z); 
    camElevation = asin(y / camRadius); 
}

// Atualizar a posição da câmera
void updateCamera() {
    float camX = camRadius * cos(camElevation) * sin(camHorizontal);
    float camY = camRadius * sin(camElevation);
    float camZ = camRadius * cos(camElevation) * cos(camHorizontal);
    

    glLoadIdentity();
    gluLookAt(camX, camY, camZ,
              config.camera.lookAt.x,config.camera.lookAt.y,config.camera.lookAt.z,
			  config.camera.up.x,config.camera.up.y,config.camera.up.z);
}


// Atualizar renderização
void renderScene() {
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
    
    updateCamera(); 

    // Desenhar eixos 
    drawAxis();

    // luz
    if (light) {
        config.drawLights();
    }

    // desenhar modelos
    glPolygonMode(GL_FRONT_AND_BACK, drawMode);
    config.group.draw(catmull, normals, light); 

    // fps
    frameCounter(); 

    glutSwapBuffers();
}

// Controlos da órbita da câmara com setas 
void processSpecialKeys(int key, int xx, int yy) {
    const float angleStep = 0.05f;
    const float zoomStep = 0.5f;

    switch (key) {
        case GLUT_KEY_LEFT: 
            camHorizontal -= angleStep; 
            break;
        case GLUT_KEY_RIGHT: 
            camHorizontal += angleStep; 
            break;
        case GLUT_KEY_UP: 
            camElevation += angleStep;
            if (camElevation > M_PI / 2 - 0.01f) 
                camElevation = M_PI / 2 - 0.01f;
            break;
        case GLUT_KEY_DOWN: 
            camElevation -= angleStep;
            if (camElevation < -M_PI / 2 + 0.01f) 
                camElevation = -M_PI / 2 + 0.01f;
            break;
    }
    glutPostRedisplay();
}

// Controlos de zoom e extras
void processNormalKeys(unsigned char key, int xx, int yy) {
    const float zoomFactor = 0.5f;

    switch (key) {
        // desativar axis
        case 'a': axis = !axis; break;
        // ajustar zoom 
        case 'i': 
            camRadius -= zoomFactor; 
            if (camRadius < 2.0f) camRadius = 2.0f;
            break;
        case 'o': 
            camRadius += zoomFactor; 
            break;
        // restart da camera
        case 'r': 
            initCamera(); 
            break;
        // Mode
        case '1': 
            drawMode = GL_FILL; 
            break;
        case '2': 
            drawMode = GL_LINE; 
            break;
        case '3': 
            drawMode = GL_POINT; 
            break;
        // órbitas
        case 'c':
			catmull = !catmull;
            break;
        // normais
        case 'n':
			normals = !normals;
			break;
        // sair
        case 27:
            exit(0);
        default: break;
    }
    glutPostRedisplay();
}

// Carregar configurações a partir do XML
void setupConfig(char* arg) {
    std::string filename = arg;

    if (filename.substr(filename.size() - 4) == ".xml") {
        config = parseConfig(filename);
    } else {
        std::cerr << "Erro: O ficheiro de entrada deve ser um XML!" << std::endl;
    }
}

// Print do guideline de utilizador
void printInfo() {
    printf("=======================================\n");
    printf("        CONTROLOS DA CÂMARA\n");
    printf("=======================================\n");
    printf("→  Setas Esquerda/Direita → Rotaciona horizontalmente a câmera\n");
    printf("→  Setas Cima/Baixo       → Rotaciona verticalmente a câmera\n");
    printf("→  Tecla 'i'              → Aproxima a câmera (Zoom In)\n");
    printf("→  Tecla 'o'              → Afasta a câmera (Zoom Out)\n");
    printf("→  Tecla 'a'              → Ativa/Desativa os eixos de referência\n");
    printf("→  Tecla 'r'              → Reinicia a posição da câmera\n");
    printf("→  Tecla '1'              → Modo de desenho: preenchido (GL_FILL)\n");
    printf("→  Tecla '2'              → Modo de desenho: wireframe (GL_LINE)\n");
    printf("→  Tecla '3'              → Modo de desenho: pontos (GL_POINT)\n");
	printf("→  Tecla 'c'              → Ativa/Desativa a visualização das órbitas\n");
	printf("→  Tecla 'n'              → Ativa/Desativa a visualização das normais\n");
    printf("→  Tecla 'ESC'            → Sair do programa\n");
    printf("=======================================\n");

    printf("\nInformações do Sistema:\n");
    printf("→ Fabricante da GPU: %s\n", glGetString(GL_VENDOR));
    printf("→ Renderer: %s\n", glGetString(GL_RENDERER));
    printf("→ Versão OpenGL: %s\n", glGetString(GL_VERSION));
}

void initGL() {

    ilInit();

    // OpenGL settings 
    glEnable(GL_DEPTH_TEST);
    glEnable(GL_CULL_FACE);
    glEnable(GL_TEXTURE_2D);
    glClearColor(0.0f, 0.0f, 0.0f, 0.0f);

    // init
    initCamera();

    // Inicializar luzes
    light = config.initLights();

    // vbos
    config.prepareAllModels();


    // Guideline
    printInfo();
}


// Função  Principal
int main(int argc, char** argv) {
    if (argc < 2) {
        std::cerr << "Uso: ./engine <ficheiro.xml>" << std::endl;
        return 1;
    }
    
    setupConfig(argv[1]);

    // Inicializar GLUT
    glutInit(&argc, argv);
    glutInitDisplayMode(GLUT_DEPTH | GLUT_DOUBLE | GLUT_RGBA);
    glutInitWindowPosition(100, 100);
    glutInitWindowSize(config.window.width, config.window.height);
    glutCreateWindow("CG Engine");

    #ifndef __APPLE__
        glewInit();
    #endif

    // Registar funções de callback do GLUT
    glutDisplayFunc(renderScene);
    glutIdleFunc(renderScene);
    glutReshapeFunc(reshape);

    // Registar Callback para teclas 
    glutSpecialFunc(processSpecialKeys);
    glutKeyboardFunc(processNormalKeys);

    initGL();

    glutMainLoop();

    return 0;
}
