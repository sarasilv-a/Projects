#ifndef GROUP_HPP
#define GROUP_HPP

#include <vector>
#include <string>
#include "model.hpp"
#include "transform.hpp"
#include "light.hpp"
#include "catmull_curve.hpp"

#ifdef __APPLE__
#include <GLUT/glut.h>
#else
#include <GL/glew.h>
#include <GL/glut.h>
#endif

class Group {
public:
    std::vector<Transform> transforms;
    std::vector<Model> models;
    std::vector<Group> children;

    Group();

    void addTransform(const Transform& transform);
    void addModel(const Model& model);
    void addChild(const Group& child);
    void draw(bool catmull, bool normals, bool lights);
    void prepareModels();
};

#endif // GROUP_HPP

