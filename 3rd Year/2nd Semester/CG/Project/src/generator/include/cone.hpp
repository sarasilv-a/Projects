#ifndef CONE_HPP
#define CONE_HPP

#include <vector>
#include <string>
#include "../../shared/include/point.hpp"
#include "../../shared/include/point2d.hpp"
#include "../../shared/include/utils.hpp"

std::vector<Point> generateCone(float radius, float height, int slices, int stacks);
void saveCone(float radius, float height, int slices, int stacks, const std::string& filename);

#endif // CONE_HPP
