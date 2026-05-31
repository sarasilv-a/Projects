#ifndef MATERIAL_HPP
#define MATERIAL_HPP

struct Material {
    float ambient[4] = {0.2f, 0.2f, 0.2f, 1.0f};
    float diffuse[4] = {0.8f, 0.8f, 0.8f, 1.0f};
    float specular[4] = {0.0f, 0.0f, 0.0f, 1.0f};
    float emission[4] = {0.0f, 0.0f, 0.0f, 1.0f};
    float shininess = 0.0f;
};


#endif // MATERIAL_HPP