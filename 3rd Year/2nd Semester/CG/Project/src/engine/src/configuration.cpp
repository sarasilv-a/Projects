#include "configuration.hpp"


Configuration::Configuration(Window window, Camera camera, Group group) {
    this->window = window;
    this->camera = camera;
    this->group = group;
	this->lights = {};
} 

Configuration::Configuration(Window window, Camera camera, Group group, std::vector<Light> lights) {
    this->window = window;
    this->camera = camera;
    this->group = group;
    this->lights = lights;
}

void Configuration::prepareAllModels() {
    group.prepareModels(); 
}

bool Configuration::initLights() {
    if (this->lights.size() > 0) {
        glEnable(GL_RESCALE_NORMAL);
        float ambient[4] = { 1.0f, 1.0f, 1.0f, 1.0f };

        glLightModelfv(GL_LIGHT_MODEL_AMBIENT, ambient);
        glEnable(GL_LIGHTING);
        for (size_t i = 0; i < this->lights.size() && i<8; i++) {
            float white[4] = { 1.0, 1.0, 1.0, 1.0 };

            glEnable(GL_LIGHT0 + i);
            glLightfv(GL_LIGHT0 + i, GL_DIFFUSE, white);
            glLightfv(GL_LIGHT0 + i, GL_SPECULAR, white);
        }
        return true;
    }

    return false;
}

void Configuration::drawLights() {
    for (size_t i = 0; i < lights.size() && i < 8; i++) {
        const Light& light = lights[i];

        if (light.type == LType::D) { // Direcional
            glLightfv(GL_LIGHT0 + i, GL_POSITION, light.dir);
        }
        else if (light.type == LType::P) { // Ponto
            glLightfv(GL_LIGHT0 + i, GL_POSITION, light.pos);
        }
        else if (light.type == LType::S) { // Spot
            glLightfv(GL_LIGHT0 + i, GL_POSITION, light.pos);
            glLightfv(GL_LIGHT0 + i, GL_SPOT_DIRECTION, light.dir);
            glLightf(GL_LIGHT0 + i, GL_SPOT_CUTOFF, light.cut);
        }
    }
}