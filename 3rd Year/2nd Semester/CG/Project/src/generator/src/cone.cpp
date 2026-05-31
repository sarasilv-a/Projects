#define _USE_MATH_DEFINES
#include <cmath>
#include "../include/cone.hpp"
#include "../../shared/include/fileUtils.hpp"

void generateCone(float radius, float height, int slices, int stacks, std::vector<Point>& points,
                                std::vector<Point>& normals,
                                std::vector<Point2D>& textures) {
    float stackHeight = height / static_cast<float>(stacks);
    float angleStep = 2.0f * static_cast<float>(M_PI) / static_cast<float>(slices);
    Point baseNormal(0.0f, -1.0f, 0.0f);

    for (int i = 0; i < slices; i++) {
        float theta1 = static_cast<float>(i) * angleStep;
        float theta2 = static_cast<float>(i + 1) * angleStep;

        // Base do cone
        points.push_back(Point(0.0f, 0.0f, 0.0f)); normals.push_back(baseNormal); textures.push_back(Point2D(0.5f, 0.5f));
        points.push_back(Point(radius * std::sin(theta2), 0.0f, radius * std::cos(theta2))); normals.push_back(baseNormal); textures.push_back(Point2D(0.5f + 0.5f * std::sin(theta2), 0.5f + 0.5f * std::cos(theta2)));
		points.push_back(Point(radius * std::sin(theta1), 0.0f, radius * std::cos(theta1))); normals.push_back(baseNormal); textures.push_back(Point2D(0.5f + 0.5f * std::sin(theta1), 0.5f + 0.5f * std::cos(theta1)));
        
        /*float faceNormal[3] = {0,0,0};*/

		float n1[3] = { 0,0,0};
		float n2[3] = { 0,0,0};
		float topn[3] = { 0,0,0 };

        for (int j = 0; j < stacks; j++) { // lateral
            float currRadius = radius * (1.0f - static_cast<float>(j) / static_cast<float>(stacks));
            float nextRadius = radius * (1.0f - static_cast<float>(j + 1) / static_cast<float>(stacks));
            float y1 = static_cast<float>(j) * stackHeight;
            float y2 = static_cast<float>(j + 1) * stackHeight;

            float u1 = static_cast<float>(i) / slices;
            float u2 = static_cast<float>(i + 1) / slices;
            float v1 = static_cast<float>(j) / stacks;
            float v2 = static_cast<float>(j + 1) / stacks;

            // Vértices
            Point p1(currRadius * sin(theta1), y1, currRadius * cos(theta1));
            Point p2(currRadius * sin(theta2), y1, currRadius * cos(theta2));
            Point p3(nextRadius * sin(theta1), y2, nextRadius * cos(theta1));
            Point p4(nextRadius * sin(theta2), y2, nextRadius * cos(theta2));

			// Normais
			if (j == 0) {
				n1[0] = sin(theta1);
				n1[1] = radius / height;
				n1[2] = cos(theta1);

				n2[0] = sin(theta2);
				n2[1] = radius / height;
				n2[2] = cos(theta2);

				normalize(n1);
				normalize(n2);
			}

            Point n1p(n1[0], n1[1], n1[2]);
            Point n2p(n2[0], n2[1], n2[2]);

			if (j == stacks - 1) {
                topn[0] = (sin(theta1) + sin(theta2)) / 2.0f;
                topn[1] = 0.0f;
                topn[2] = (cos(theta1) + cos(theta2)) / 2.0f;
                normalize(topn);
				Point topnp(topn[0], topn[1], topn[2]);

                points.push_back(p1); normals.push_back(n1p); textures.push_back(Point2D(u1, v1));
                points.push_back(p2); normals.push_back(n2p); textures.push_back(Point2D(u2, v1));
                points.push_back(p3); normals.push_back(topnp); textures.push_back(Point2D(u1, v2));
			}

            /*if (j == 0) {
                float a1[3] = { p1.x, p1.y, p1.z };
                float b1[3] = { p2.x, p2.y, p2.z };
                float c1[3] = { p3.x, p3.y, p3.z };
                computeNormal(a1, b1, c1, faceNormal);
            }
            Point n1(faceNormal[0],faceNormal[1],faceNormal[2]);*/
            else {
                // Triângulo 1
                points.push_back(p1); normals.push_back(n1p); textures.push_back(Point2D(u1, v1));
                points.push_back(p2); normals.push_back(n2p); textures.push_back(Point2D(u2, v1));
                points.push_back(p3); normals.push_back(n1p); textures.push_back(Point2D(u1, v2));

                // Triângulo 2
                points.push_back(p2); normals.push_back(n2p); textures.push_back(Point2D(u2, v1));
                points.push_back(p4); normals.push_back(n2p); textures.push_back(Point2D(u2, v2));
                points.push_back(p3); normals.push_back(n1p); textures.push_back(Point2D(u1, v2));
            }
        }
    }

}


void saveCone(float radius, float height, int slices, int stacks, const std::string& filename) {
    std::vector<Point> points;
    std::vector<Point> normals;
    std::vector<Point2D> textures;
    generateCone(radius, height, slices, stacks, points, normals, textures);
    saveToFileExtended(points, normals, textures, filename);
}
