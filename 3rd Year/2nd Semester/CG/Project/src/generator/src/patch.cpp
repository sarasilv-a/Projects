#include "../include/patch.hpp"

void binomial(float t, float* b) {
    float it = 1 - t;
    b[0] = it * it * it;
    b[1] = 3 * t * it * it;
    b[2] = 3 * t * t * it;
    b[3] = t * t * t;
}

void binomialDeriv(float t, float* b) {
    float it = 1 - t;
    b[0] = -3 * it * it;
    b[1] = 3 * it * it - 6 * t * it;
    b[2] = 6 * t * it - 3 * t * t;
    b[3] = 3 * t * t;
}

Point bezierPoint(float u, float v, float controlPoints[4][4][3]) {
    Point p(0, 0, 0);
    float bu[4], bv[4];
    binomial(u, bu);
    binomial(v, bv);
    for (int i = 0; i < 4; ++i) {
        for (int j = 0; j < 4; ++j) {
            float b = bu[i] * bv[j];
            p.x += controlPoints[i][j][0] * b;
            p.y += controlPoints[i][j][1] * b;
            p.z += controlPoints[i][j][2] * b;
        }
    }
    return p;
}

Point bezierNormal(float u, float v, float controlPoints[4][4][3]) {
    float bu[4], bv[4], dbu[4], dbv[4];
    binomial(u, bu); binomial(v, bv);
    binomialDeriv(u, dbu); binomialDeriv(v, dbv);

    float du[3] = { 0, 0, 0 };
    float dv[3] = { 0, 0, 0 };

    for (int i = 0; i < 4; i++) {
        for (int j = 0; j < 4; j++) {
            float* p = controlPoints[i][j];
            float buv = bu[i] * dbv[j];
            float dbuv = dbu[i] * bv[j];

            du[0] += dbuv * p[0];
            du[1] += dbuv * p[1];
            du[2] += dbuv * p[2];

            dv[0] += buv * p[0];
            dv[1] += buv * p[1];
            dv[2] += buv * p[2];
        }
    }

    float normal[3];
    cross(dv, du, normal);
    normalize(normal);
    return Point(normal[0], normal[1], normal[2]);
}

void generatePatch(const std::string& patchFile, int tessellation, std::vector<Point>& points,
                    std::vector<Point>& normals,
                    std::vector<Point2D>& textures) {

    std::string fullPath = PDIR + patchFile;
    std::ifstream file(fullPath);
    std::vector<Point> result;

    if (!file.is_open()) {
        std::cerr << "Erro ao abrir ficheiro de patch: " << patchFile << std::endl;
        return;
    }

    size_t numPatches;
    file >> numPatches;
    std::vector<std::vector<size_t>> patches(numPatches, std::vector<size_t>(16));

    for (size_t i = 0; i < numPatches; ++i) {
        for (size_t j = 0; j < 16; ++j) {
            size_t idx;
            file >> idx;
            file.ignore();
            patches[i][j] = idx;
        }
    }

    size_t numPoints;
    file >> numPoints;
    std::vector<Point> controlPoints;
    for (size_t i = 0; i < numPoints; ++i) {
        float x, y, z;
        file >> x;
        file.ignore();
        file >> y;
        file.ignore();
        file >> z;
        file.ignore();
        controlPoints.push_back(Point(x, y, z));
    }

    file.close();

    for (const auto& patch : patches) {
        float patchPoints[4][4][3];
        for (int u = 0; u < 4; u++) {
            for (int v = 0; v < 4; v++) {
                Point p = controlPoints[patch[u * 4 + v]];
                patchPoints[u][v][0] = p.x;
                patchPoints[u][v][1] = p.y;
                patchPoints[u][v][2] = p.z;
            }
        }

        for (int i = 0; i < tessellation; i++) {
            for (int j = 0; j < tessellation; j++) {
        
                float u = (float)i / tessellation;
                float v = (float)j / tessellation;
                float u1 = (float)(i + 1) / tessellation;
                float v1 = (float)(j + 1) / tessellation;

                Point2D texCoord1(u, v);
                Point2D texCoord2(u1, v);
                Point2D texCoord3(u, v1);
                Point2D texCoord4(u1, v1);

                Point p1 = bezierPoint(u, v, patchPoints);
                Point p2 = bezierPoint(u1, v, patchPoints);
                Point p3 = bezierPoint(u, v1, patchPoints);
                Point p4 = bezierPoint(u1, v1, patchPoints);

                Point n1 = bezierNormal(u, v, patchPoints);
                Point n2 = bezierNormal(u1, v, patchPoints);
                Point n3 = bezierNormal(u, v1, patchPoints);
                Point n4 = bezierNormal(u1, v1, patchPoints);

                // Triângulo 1
                points.push_back(p1); normals.push_back(n1); textures.push_back(Point2D(u, v));
                points.push_back(p3); normals.push_back(n3); textures.push_back(Point2D(u, v1));
                points.push_back(p2); normals.push_back(n2); textures.push_back(Point2D(u1, v));

                // Triângulo 2
                points.push_back(p2); normals.push_back(n2); textures.push_back(Point2D(u1, v));
                points.push_back(p3); normals.push_back(n3); textures.push_back(Point2D(u, v1));
                points.push_back(p4); normals.push_back(n4); textures.push_back(Point2D(u1, v1));



            }
        }
    }
}

void savePatch(const std::string& patchFile, int tessellation, const std::string& outputFile) {
    std::vector<Point> points;
    std::vector<Point> normals;
    std::vector<Point2D> textures;
    generatePatch(patchFile, tessellation, points, normals, textures);
	if (points.empty() || normals.empty() || textures.empty()) {
		std::cerr << "Erro ao gerar o patch: " << patchFile << std::endl;
		return;
	}
    saveToFileExtended(points, normals, textures, outputFile);
}
