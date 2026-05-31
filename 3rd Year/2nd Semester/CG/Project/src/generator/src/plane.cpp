#include "../include/plane.hpp"
#include "../../shared/include/fileUtils.hpp"
#include <vector>

std::vector<Point> generatePlane(float size, int divisions,
                                 std::vector<Point>& normals,
                                 std::vector<Point2D>& textures) {
    float half = size / 2.0f;
    float step = size / static_cast<float>(divisions);
    std::vector<Point> points;
    Point normal(0.0f, 1.0f, 0.0f);

    for (int i = 0; i < divisions; i++) {
        for (int j = 0; j < divisions; j++) {
            float x1 = -half + j * step;
            float z1 = -half + i * step;
            float x2 = x1 + step;
            float z2 = z1 + step;

            // Coordenadas de textura
            float u1 = static_cast<float>(j) / divisions;
            float v1 = static_cast<float>(i) / divisions;
            float u2 = static_cast<float>(j + 1) / divisions;
            float v2 = static_cast<float>(i + 1) / divisions;

            // Triângulo 1
            points.push_back(Point(x1, 0.0f, z1));
            normals.push_back(normal);
            textures.push_back(Point2D(u1, v1));

            points.push_back(Point(x1, 0.0f, z2));
            normals.push_back(normal);
            textures.push_back(Point2D(u1, v2));

            points.push_back(Point(x2, 0.0f, z2));
            normals.push_back(normal);
            textures.push_back(Point2D(u2, v2));

            // Triângulo 2
            points.push_back(Point(x1, 0.0f, z1));
            normals.push_back(normal);
            textures.push_back(Point2D(u1, v1));

            points.push_back(Point(x2, 0.0f, z2));
            normals.push_back(normal);
            textures.push_back(Point2D(u2, v2));

            points.push_back(Point(x2, 0.0f, z1));
            normals.push_back(normal);
            textures.push_back(Point2D(u2, v1));
        }
    }

    return points;
}

void savePlane(float size, int divisions, const std::string& filename) {
    std::vector<Point> normals;
    std::vector<Point2D> textures;
    std::vector<Point> points = generatePlane(size, divisions, normals, textures);
    saveToFileExtended(points, normals, textures, filename);
}
