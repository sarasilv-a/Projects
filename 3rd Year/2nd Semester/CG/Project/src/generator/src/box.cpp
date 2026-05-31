#include "../include/box.hpp"
#include "../../shared/include/fileUtils.hpp"

std::vector<Point> generateBox(float length, int divisions,
    std::vector<Point>& normals,
    std::vector<Point2D>& textures) {

    float half = length / 2.0f;
    float step = length / static_cast<float>(divisions);
    std::vector<Point> points;

    for (int i = 0; i < divisions; i++) {
        for (int j = 0; j < divisions; j++) {
            float x1 = -half + static_cast<float>(j) * step;
            float y1 = -half;
            float z1 = -half + static_cast<float>(i) * step;
            float x2 = x1 + step;
            float z2 = z1 + step;

            float u1 = static_cast<float>(j) / divisions;
            float v1 = static_cast<float>(i) / divisions;
            float u2 = static_cast<float>(j + 1) / divisions;
            float v2 = static_cast<float>(i + 1) / divisions;

            // Base y = -half
            Point n(0, -1, 0);
            points.push_back(Point(x1, y1, z1)); normals.push_back(n); textures.push_back(Point2D(u1, v1));
            points.push_back(Point(x2, y1, z1)); normals.push_back(n); textures.push_back(Point2D(u2, v1));
            points.push_back(Point(x1, y1, z2)); normals.push_back(n); textures.push_back(Point2D(u1, v2));

            points.push_back(Point(x2, y1, z2)); normals.push_back(n); textures.push_back(Point2D(u2, v2));
            points.push_back(Point(x1, y1, z2)); normals.push_back(n); textures.push_back(Point2D(u1, v2));
            points.push_back(Point(x2, y1, z1)); normals.push_back(n); textures.push_back(Point2D(u2, v1));

            // Base y = +half
            float y2 = half;
            n = Point(0, 1, 0);
            points.push_back(Point(x1, y2, z2)); normals.push_back(n); textures.push_back(Point2D(u1, v2));
            points.push_back(Point(x2, y2, z2)); normals.push_back(n); textures.push_back(Point2D(u2, v2));
            points.push_back(Point(x1, y2, z1)); normals.push_back(n); textures.push_back(Point2D(u1, v1));

            points.push_back(Point(x1, y2, z1)); normals.push_back(n); textures.push_back(Point2D(u1, v1));
            points.push_back(Point(x2, y2, z2)); normals.push_back(n); textures.push_back(Point2D(u2, v2));
            points.push_back(Point(x2, y2, z1)); normals.push_back(n); textures.push_back(Point2D(u2, v1));

            // Face z = -half
            float z3 = -half;
            float x3 = -half + static_cast<float>(j) * step;
            float x4 = x3 + step;
            float y3 = -half + static_cast<float>(i) * step;
            float y4 = y3 + step;

            n = Point(0, 0, -1);
            points.push_back(Point(x3, y3, z3)); normals.push_back(n); textures.push_back(Point2D(u1, v1));
            points.push_back(Point(x3, y4, z3)); normals.push_back(n); textures.push_back(Point2D(u1, v2));
            points.push_back(Point(x4, y4, z3)); normals.push_back(n); textures.push_back(Point2D(u2, v2));

            points.push_back(Point(x3, y3, z3)); normals.push_back(n); textures.push_back(Point2D(u1, v1));
            points.push_back(Point(x4, y4, z3)); normals.push_back(n); textures.push_back(Point2D(u2, v2));
            points.push_back(Point(x4, y3, z3)); normals.push_back(n); textures.push_back(Point2D(u2, v1));

            // Face z = +half
            float z4 = half;
            n = Point(0, 0, 1);
            points.push_back(Point(x4, y3, z4)); normals.push_back(n); textures.push_back(Point2D(u2, v1));
            points.push_back(Point(x3, y4, z4)); normals.push_back(n); textures.push_back(Point2D(u1, v2));
            points.push_back(Point(x3, y3, z4)); normals.push_back(n); textures.push_back(Point2D(u1, v1));

            points.push_back(Point(x4, y3, z4)); normals.push_back(n); textures.push_back(Point2D(u2, v1));
            points.push_back(Point(x4, y4, z4)); normals.push_back(n); textures.push_back(Point2D(u2, v2));
            points.push_back(Point(x3, y4, z4)); normals.push_back(n); textures.push_back(Point2D(u1, v2));

            // Face x = -half
            float x5 = -half;
            float y5 = -half + static_cast<float>(i) * step;
            float y6 = y5 + step;
            float z5 = -half + static_cast<float>(j) * step;
            float z6 = z5 + step;

            n = Point(-1, 0, 0);
            points.push_back(Point(x5, y5, z5)); normals.push_back(n); textures.push_back(Point2D(u1, v1));
            points.push_back(Point(x5, y5, z6)); normals.push_back(n); textures.push_back(Point2D(u2, v1));
            points.push_back(Point(x5, y6, z5)); normals.push_back(n); textures.push_back(Point2D(u1, v2));

            points.push_back(Point(x5, y6, z6)); normals.push_back(n); textures.push_back(Point2D(u2, v2));
            points.push_back(Point(x5, y6, z5)); normals.push_back(n); textures.push_back(Point2D(u1, v2));
            points.push_back(Point(x5, y5, z6)); normals.push_back(n); textures.push_back(Point2D(u2, v1));

            // Face x = +half
            float x6 = half;
            n = Point(1, 0, 0);
            points.push_back(Point(x6, y5, z5)); normals.push_back(n); textures.push_back(Point2D(u1, v1));
            points.push_back(Point(x6, y6, z6)); normals.push_back(n); textures.push_back(Point2D(u2, v2));
            points.push_back(Point(x6, y5, z6)); normals.push_back(n); textures.push_back(Point2D(u2, v1));

            points.push_back(Point(x6, y5, z5)); normals.push_back(n); textures.push_back(Point2D(u1, v1));
            points.push_back(Point(x6, y6, z5)); normals.push_back(n); textures.push_back(Point2D(u1, v2));
            points.push_back(Point(x6, y6, z6)); normals.push_back(n); textures.push_back(Point2D(u2, v2));
        }
    }

    return points;
}

void saveBox(float length, int divisions, const std::string& filename) {
    std::vector<Point> normals;
    std::vector<Point2D> textures;
    std::vector<Point> points = generateBox(length, divisions, normals, textures);
    saveToFileExtended(points, normals, textures, filename);
}