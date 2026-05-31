#ifndef HELIX_HPP
#define HELIX_HPP

#include <string>
#include "../../shared/include/fileUtils.hpp"
#include "../../shared/include/utils.hpp"
#include "../../shared/include/point.hpp"
#include "../../shared/include/point2d.hpp"
#include <vector>
#include <iostream>
#include <cmath>

void saveHelix(float radius, float height, int turns, int slices, const std::string& filename);

#endif
