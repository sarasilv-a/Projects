#define _USE_MATH_DEFINES
#include <cmath>
#include "helix.hpp"
#include "../../shared/include/fileUtils.hpp"
#include <vector>
#include <iostream>

void generateHelix(float radius, float height, int turns, int slices, std::vector<Point>& points,
    std::vector<Point>& normals,
    std::vector<Point2D>& textures) {

    float height2 = -height / 2.0f;
    float step = (2.0f * static_cast<float>(M_PI)) / static_cast<float>(slices);
    float heightStep = height / static_cast<float>(turns * slices);

    for (int i = 0; i < turns * slices; ++i) {
        float angle1 = static_cast<float>(i) * step;
        float angle2 = static_cast<float>(i + 1) * step;
        float h1 = height2 + static_cast<float>(i) * heightStep;
        float h2 = height2 + static_cast<float>(i + 1) * heightStep;

        float x1 = radius * std::cos(angle1);
        float y1 = h1;
        float z1 = radius * std::sin(angle1);

        float x2 = radius * std::cos(angle2);
        float y2 = h2;
        float z2 = radius * std::sin(angle2);

        Point p1(x1, y1, z1);
        Point p2(x1, y1 + 0.1f, z1);
        Point p3(x2, y2, z2);
        Point p4(x2, y2 + 0.1f, z2);

        float a[3], b[3], c[3], n[3];

        // Parte externa - triângulo 1
        points.push_back(p1);
        points.push_back(p2);
        points.push_back(p3);

        a[0] = p1.x; a[1] = p1.y; a[2] = p1.z;
        b[0] = p2.x; b[1] = p2.y; b[2] = p2.z;
        c[0] = p3.x; c[1] = p3.y; c[2] = p3.z;
        computeNormal(a, b, c, n);
        normals.push_back(Point(n[0], n[1], n[2]));
        normals.push_back(Point(n[0], n[1], n[2]));
        normals.push_back(Point(n[0], n[1], n[2]));

        textures.push_back(Point2D(static_cast<float>(angle1 / (2 * M_PI)), (y1 + height / 2) / height));
        textures.push_back(Point2D(static_cast<float>(angle1 / (2 * M_PI)), (y1 + 0.1f + height / 2) / height));
        textures.push_back(Point2D(static_cast<float>(angle2 / (2 * M_PI)), (y2 + height / 2) / height));

        // Parte externa - triângulo 2
        points.push_back(p3);
        points.push_back(p2);
        points.push_back(p4);

        a[0] = p3.x; a[1] = p3.y; a[2] = p3.z;
        b[0] = p2.x; b[1] = p2.y; b[2] = p2.z;
        c[0] = p4.x; c[1] = p4.y; c[2] = p4.z;
        computeNormal(a, b, c, n);
        normals.push_back(Point(n[0], n[1], n[2]));
        normals.push_back(Point(n[0], n[1], n[2]));
        normals.push_back(Point(n[0], n[1], n[2]));

        textures.push_back(Point2D(static_cast<float>(angle2 / (2 * M_PI)), (y2 + height / 2) / height));
        textures.push_back(Point2D(static_cast<float>(angle1 / (2 * M_PI)), (y1 + 0.1f + height / 2) / height));
        textures.push_back(Point2D(static_cast<float>(angle2 / (2 * M_PI)), (y2 + 0.1f + height / 2) / height));

        // Parte interna - triângulo 3
        points.push_back(p3);
        points.push_back(p2);
        points.push_back(p1);

        a[0] = p3.x; a[1] = p3.y; a[2] = p3.z;
        b[0] = p2.x; b[1] = p2.y; b[2] = p2.z;
        c[0] = p1.x; c[1] = p1.y; c[2] = p1.z;
        computeNormal(a, b, c, n);
        normals.push_back(Point(n[0], n[1], n[2]));
        normals.push_back(Point(n[0], n[1], n[2]));
        normals.push_back(Point(n[0], n[1], n[2]));

        textures.push_back(Point2D(static_cast<float>(angle2 / (2 * M_PI)), (y2 + height / 2) / height));
        textures.push_back(Point2D(static_cast<float>(angle1 / (2 * M_PI)), (y1 + 0.1f + height / 2) / height));
        textures.push_back(Point2D(static_cast<float>(angle1 / (2 * M_PI)), (y1 + height / 2) / height));

        // Parte interna - triângulo 4
        points.push_back(p4);
        points.push_back(p2);
        points.push_back(p3);

        a[0] = p4.x; a[1] = p4.y; a[2] = p4.z;
        b[0] = p2.x; b[1] = p2.y; b[2] = p2.z;
        c[0] = p3.x; c[1] = p3.y; c[2] = p3.z;
        computeNormal(a, b, c, n);
        normals.push_back(Point(n[0], n[1], n[2]));
        normals.push_back(Point(n[0], n[1], n[2]));
        normals.push_back(Point(n[0], n[1], n[2]));

        textures.push_back(Point2D(static_cast<float>(angle2 / (2 * M_PI)), (y2 + 0.1f + height / 2) / height));
        textures.push_back(Point2D(static_cast<float>(angle1 / (2 * M_PI)), (y1 + 0.1f + height / 2) / height));
        textures.push_back(Point2D(static_cast<float>(angle2 / (2 * M_PI)), (y2 + height / 2) / height));
    }
}



void saveHelix(float radius, float height, int turns, int slices, const std::string& filename) {
    std::vector<Point> points;
    std::vector<Point> normals;
    std::vector<Point2D> textures;
    generateHelix(radius, height, turns, slices, points, normals, textures);
    saveToFileExtended(points, normals, textures, filename);
}
