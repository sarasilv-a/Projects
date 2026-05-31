#define _USE_MATH_DEFINES
#include <cmath>
#include "../include/sphere.hpp"
#include "../../shared/include/fileUtils.hpp"

void generateSphere(float radius, int slices, int stacks, std::vector<Point>& points,
                                std::vector<Point>& normals,
                                std::vector<Point2D>& textures) {

    float stackStep = static_cast<float>(M_PI) / static_cast<float>(stacks);      
    float sliceStep = (2.0f * static_cast<float>(M_PI)) / static_cast<float>(slices);

    for (int i = 0; i < stacks; i++) {
        float theta1 = static_cast<float>(i) * stackStep;
        float theta2 = static_cast<float>(i + 1) * stackStep;

        for (int j = 0; j < slices; j++) {
            float phi1 = static_cast<float>(j) * sliceStep;
            float phi2 = static_cast<float>(j + 1) * sliceStep;

            float u1 = phi1 / (2.0f * static_cast<float>(M_PI));
            float u2 = phi2 / (2.0f * static_cast<float>(M_PI));
            float v1 = theta1 / static_cast<float>(M_PI);
            float v2 = theta2 / static_cast<float>(M_PI);

            // Ponto 1
            float x1 = radius * std::sin(theta1) * std::sin(phi1);
            float z1 = radius * std::sin(theta1) * std::cos(phi1);
            float y1 = radius * std::cos(theta1);
            Point p1(x1, y1, z1);
            float n1[3] = { x1, y1, z1 };
            normalize(n1);
            Point normal1(n1[0], n1[1], n1[2]);
			Point2D texture1(u1, v1);

            // Ponto 2
            float x2 = radius * std::sin(theta1) * std::sin(phi2);
            float z2 = radius * std::sin(theta1) * std::cos(phi2);
            float y2 = radius * std::cos(theta1);
            Point p2(x2, y2, z2);
            float n2[3] = { x2, y2, z2 };
            normalize(n2);
            Point normal2(n2[0], n2[1], n2[2]);
            Point2D texture2(u2, v1);

            // Ponto 3
            float x3 = radius * std::sin(theta2) * std::sin(phi1);
            float z3 = radius * std::sin(theta2) * std::cos(phi1);
            float y3 = radius * std::cos(theta2);
            Point p3(x3, y3, z3);
            float n3[3] = { x3, y3, z3 };
            normalize(n3);
            Point normal3(n3[0], n3[1], n3[2]);
            Point2D texture3(u1, v2);

            // Ponto 4
            float x4 = radius * std::sin(theta2) * std::sin(phi2);
            float z4 = radius * std::sin(theta2) * std::cos(phi2);
            float y4 = radius * std::cos(theta2);
            Point p4(x4, y4, z4);
            float n4[3] = { x4, y4, z4 };
            normalize(n4);
            Point normal4(n4[0], n4[1], n4[2]);
            Point2D texture4(u2, v2);

            // Triângulo 1
			points.push_back(p1); normals.push_back(normal1); textures.push_back(texture1);
			points.push_back(p4); normals.push_back(normal4); textures.push_back(texture4);
			points.push_back(p2); normals.push_back(normal2); textures.push_back(texture2);

            // Triângulo 2
			points.push_back(p1); normals.push_back(normal1); textures.push_back(texture1);
			points.push_back(p3); normals.push_back(normal3); textures.push_back(texture3);
			points.push_back(p4); normals.push_back(normal4); textures.push_back(texture4);
        }
    }
}

void saveSphere(float radius, int slices, int stacks, const std::string& filename) {
    std::vector<Point> points;
    std::vector<Point> normals;
    std::vector<Point2D> textures;
    generateSphere(radius, slices, stacks, points, normals, textures);
    saveToFileExtended(points, normals, textures, filename);
}
