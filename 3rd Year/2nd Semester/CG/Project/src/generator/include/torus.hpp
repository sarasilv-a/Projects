#ifndef TORUS_HPP
#define TORUS_HPP

#include <vector>
#include "../../shared/include/point.hpp"
#include "../../shared/include/point2D.hpp"
#include "../../shared/include/utils.hpp"
#include "../../shared/include/fileUtils.hpp"
#include <string>

bool saveTorus(float majorRadius, float minorRadius, int sides, int rings, const std::string& filepath);
void generateTorus(float majorRadius, float minorRadius, int sides, int rings, std::vector<Point>& points, std::vector<Point>& normals, std::vector<Point2D>& textures);

#endif // TORUS_HPP
