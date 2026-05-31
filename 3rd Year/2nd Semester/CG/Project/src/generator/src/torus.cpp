#define _USE_MATH_DEFINES
#include <cmath>
#include <iostream>
#include "torus.hpp"

void generateTorus(float majorRadius, float minorRadius, int sides, int rings, std::vector<Point>& points, std::vector<Point>& normals, std::vector<Point2D>& textures) {

    for (int i = 0; i < rings; ++i) {
        float theta1 = static_cast<float>(i) * 2.0f * static_cast<float>(M_PI) / static_cast<float>(rings);
        float theta2 = static_cast<float>(i + 1) * 2.0f * static_cast<float>(M_PI) / static_cast<float>(rings);

        for (int j = 0; j < sides; ++j) {
            float phi1 = static_cast<float>(j) * 2.0f * static_cast<float>(M_PI) / static_cast<float>(sides);
            float phi2 = static_cast<float>(j + 1) * 2.0f * static_cast<float>(M_PI) / static_cast<float>(sides);

            float u1 = static_cast<float>(j) / static_cast<float>(sides);
            float u2 = static_cast<float>(j + 1) / static_cast<float>(sides);
            float v1 = static_cast<float>(i) / static_cast<float>(rings);
            float v2 = static_cast<float>(i + 1) / static_cast<float>(rings);

            // Vértices
			// Ponto 1
            float x1 = (majorRadius + minorRadius * std::cos(phi1)) * std::cos(theta1);
            float y1 = minorRadius * std::sin(phi1);
            float z1 = (majorRadius + minorRadius * std::cos(phi1)) * std::sin(theta1);
			Point p1 = Point(x1, y1, z1);
            // (majorRadius * cos(theta1), 0, (majorRadius * sin(theta1))) = C centro do tubo do torus
            // P - C = vetor da normal  
            float normal1[3] = {x1 - majorRadius * cos(theta1), y1, z1 - majorRadius * sin(theta1)};
            normalize(normal1);
			Point n1 = Point(normal1[0], normal1[1], normal1[2]);
			Point2D t1 = Point2D(u1, v1);

            //Ponto 2
            float x2 = (majorRadius + minorRadius * std::cos(phi2)) * std::cos(theta1);
            float y2 = minorRadius * std::sin(phi2);
            float z2 = (majorRadius + minorRadius * std::cos(phi2)) * std::sin(theta1);
			Point p2 = Point(x2, y2, z2);
            float normal2[3] = { x2 - majorRadius * cos(theta1), y2, z2 - majorRadius * sin(theta1) };
            normalize(normal2);
            Point n2 = Point(normal2[0], normal2[1], normal2[2]);
            Point2D t2 = Point2D(u2, v1);

			// Ponto 3
            float x3 = (majorRadius + minorRadius * std::cos(phi1)) * std::cos(theta2);
            float y3 = minorRadius * std::sin(phi1);
            float z3 = (majorRadius + minorRadius * std::cos(phi1)) * std::sin(theta2);
			Point p3 = Point(x3, y3, z3);
            float normal3[3] = { x3 - majorRadius * cos(theta2), y3, z3 - majorRadius * sin(theta2) };
            normalize(normal3);
            Point n3 = Point(normal3[0], normal3[1], normal3[2]);
            Point2D t3 = Point2D(u1, v2);

			// Ponto 4
            float x4 = (majorRadius + minorRadius * std::cos(phi2)) * std::cos(theta2);
            float y4 = minorRadius * std::sin(phi2);
            float z4 = (majorRadius + minorRadius * std::cos(phi2)) * std::sin(theta2);
			Point p4 = Point(x4, y4, z4);
            float normal4[3] = { x4 - majorRadius * cos(theta2), y4, z4 - majorRadius * sin(theta2) };
            normalize(normal4);
            Point n4 = Point(normal4[0], normal4[1], normal4[2]);   
            Point2D t4 = Point2D(u2, v2);

          
            // triângulos
			points.push_back(p1); normals.push_back(n1); textures.push_back(t1);
			points.push_back(p2); normals.push_back(n2); textures.push_back(t2);
			points.push_back(p4); normals.push_back(n4); textures.push_back(t4);

			points.push_back(p1); normals.push_back(n1); textures.push_back(t1);
			points.push_back(p4); normals.push_back(n4); textures.push_back(t4);
			points.push_back(p3); normals.push_back(n3); textures.push_back(t3);
        }
    }

}

bool saveTorus(float majorRadius, float minorRadius, int sides, int rings, const std::string& filepath) {
    std::vector<Point> points; 
    std::vector<Point> normals;
    std::vector<Point2D> textures;
    generateTorus(majorRadius, minorRadius, sides, rings, points, normals, textures);

    if (points.empty() || normals.empty() || textures.empty()) {
        std::cerr << "Erro: Torus não gerado corretamente.\n";
        return false;
    }

    saveToFileExtended(points, normals, textures, filepath);
    return true;
}
