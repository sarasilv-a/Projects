#ifndef SPHERE_HPP
#define SPHERE_HPP

#include <vector>
#include <string>
#include "../../shared/include/point2d.hpp"
#include "../../shared/include/point.hpp"
#include "../../shared/include/utils.hpp"

void generateSphere(float radius, int slices, int stacks, std::vector<Point>& points,
                    std::vector<Point>& normals,
                    std::vector<Point2D>& textures);
void saveSphere(float radius, int slices, int stacks, const std::string& filename);

#endif // SPHERE_HPP
