#ifndef FILE_UTILS_HPP
#define FILE_UTILS_HPP

#include <vector>
#include <string>
#include "point.hpp"
#include "point2d.hpp"

void saveToFile(const std::vector<Point>& points, const std::string& filepath);
std::vector<Point> parse3Dfile(const std::string& filepath);
void parse3DfileExtended(const std::string& filepath,
    std::vector<Point>& vertices,
    std::vector<Point>& normals,
    std::vector<Point2D>& textures);
std::vector<Point> parseOBJfile(const std::string& filepath);
void parseFile(const std::string& filepath, std::vector<Point>& vertices,
    std::vector<Point>& normals,
    std::vector<Point2D>& textures);
void saveToFileExtended(const std::vector<Point>& vertices,
                        const std::vector<Point>& normals,
                        const std::vector<Point2D>& textures,
                        const std::string& filename);

#endif // FILE_UTILS_HPP
