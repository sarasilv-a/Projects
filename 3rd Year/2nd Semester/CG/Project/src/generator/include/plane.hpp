#ifndef PLANE_HPP
#define PLANE_HPP

#include <vector>
#include <string>
#include "../../shared/include/point.hpp"
#include "../../shared/include/point2d.hpp"

// Função que gera os vértices de um plano
std::vector<Point> generatePlane(float size, int divisions,
    std::vector<Point>& normals,
    std::vector<Point2D>& textures);

// Função que gera um plano e guarda num ficheiro
void savePlane(float size, int divisions, const std::string& filename);

#endif  // PLANE_HPP
