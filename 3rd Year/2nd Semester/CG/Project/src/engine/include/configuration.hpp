#ifndef CONFIGURATION_HPP
#define CONFIGURATION_HPP

#include "window.hpp"
#include "camera.hpp"
#include "group.hpp"
#include "light.hpp"
#include <vector>
#include <string>

class Configuration {
public:
    Window window;
    Camera camera;
    std::vector<Light> lights;
    Group group;

    Configuration() {}
    Configuration(Window window, Camera camera, Group group);
    Configuration(Window window, Camera camera, Group group, std::vector<Light> lights);

    bool initLights();
    void drawLights();
    void prepareAllModels();
};

#endif // CONFIGURATION_HPP
