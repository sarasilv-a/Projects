#ifndef BOX_HPP
#define BOX_HPP

#include <vector>
#include <string>
#include "../../shared/include/point.hpp"
#include "../../shared/include/point2d.hpp"

std::vector<Point> generateBox(float length, int divisions,
    std::vector<Point>& normals,
    std::vector<Point2D>& textures);
void saveBox(float length, int divisions, const std::string& filename);

#endif // BOX_HPP
