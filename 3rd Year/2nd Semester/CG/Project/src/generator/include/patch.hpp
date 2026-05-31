#ifndef PATCH_HPP
#define PATCH_HPP

#include <vector>
#include <string>
#include <cmath>
#include <fstream>
#include <iostream>

#include "../../shared/include/fileUtils.hpp"
#include "../../shared/include/point.hpp"
#include "../../shared/include/point2d.hpp"
#include "../../shared/include/utils.hpp"

#define PDIR "../src/patches/"

void generatePatch(const std::string& patchFile, int tessellation, std::vector<Point>& points,
                                std::vector<Point>& normals,
                                std::vector<Point2D>& textures);
void savePatch(const std::string& patchFile, int tessel, const std::string& filename);

#endif // PATCH_HPP
