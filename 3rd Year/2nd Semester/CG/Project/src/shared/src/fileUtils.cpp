#include "../include/fileUtils.hpp"
#include <fstream>
#include <iostream>
#include <sstream>
#include <string>
#include <vector>

#define DIR "../src/models/"

void saveToFile(const std::vector<Point>& points, const std::string& filepath) {
    std::string fullPath = DIR + filepath;
    std::cout << "Tentando salvar o ficheiro em: " << fullPath << std::endl;
    std::ofstream file(fullPath);

    if (file.is_open()) {
        file << points.size() << std::endl;
        for (const auto& point : points) {
            file << point.x << " " << point.y << " " << point.z << "\n";
        }
        file.close();
        std::cout << "Ficheiro guardado: " << fullPath << std::endl;
    } else {
        std::cerr << "Erro ao abrir o ficheiro " << fullPath << std::endl;
    }
}

std::vector<Point> parse3Dfile(const std::string& filepath) {
    std::vector<Point> points;
    std::ifstream file(filepath);

    if (!file.is_open()) {
        std::cerr << "Erro ao abrir " << filepath << std::endl;
        return points;
    }

    int numPoints;
    file >> numPoints;

    float x, y, z;
    while (file >> x >> y >> z) {
        points.push_back(Point(x, y, z));
    }

    file.close();
    return points;
}

void parse3DfileExtended(const std::string& filepath,
    std::vector<Point>& vertices,
    std::vector<Point>& normals,
    std::vector<Point2D>& textures) {
    std::ifstream file(filepath);
    if (!file.is_open()) {
        std::cerr << "Erro ao abrir ficheiro: " << filepath << std::endl;
        return;
    }

    char hash;
    int numPoints;
    file >> hash >> numPoints;
	if (hash != '#') {
		std::cerr << "Formato inválido no ficheiro: " << filepath << std::endl;
		file.close();
		return;
	}

    // Lê os dados de cada ponto
    char tag;
    float x, y, z, nx, ny, nz, u, v;
    while (file >> tag >> x >> y >> z >> nx >> ny >> nz >> u >> v) {
        if (tag != 'p') continue;

        vertices.push_back(Point(x, y, z));
        normals.push_back(Point(nx, ny, nz));
        textures.push_back(Point2D(u, v));
    }

    file.close();
}



std::vector<Point> parseOBJfile(const std::string& filepath) {
    std::vector<Point> points;            // Todos os vértices
    std::vector<Point> orderedPoints;     // Vértices ordenados por faces
    std::ifstream file(filepath);

    if (!file.is_open()) {
        std::cerr << "Erro ao abrir " << filepath << std::endl;
        return orderedPoints;
    }

    std::string line;
    while (std::getline(file, line)) {
        std::istringstream iss(line);
        std::string type;
        iss >> type;

        if (type == "v") {
            Point point;
            iss >> point.x >> point.y >> point.z;
            points.push_back(point);
        } 
        else if (type == "f") {
            std::string vertex;
            std::vector<int> indices;

            while (iss >> vertex) {
                size_t slashPos = vertex.find('/');
                std::string indexStr = vertex.substr(0, slashPos);
                int index = std::stoi(indexStr) - 1; // OBJ é 1-based
                indices.push_back(index);
            }

            // Guardar vértices das faces
            for (int idx : indices) {
                if (idx >= 0 && static_cast<size_t>(idx) < points.size()) {
                    orderedPoints.push_back(points[idx]);
                }
            }
        }
    }

    file.close();
    return orderedPoints;
}

void parseFile(const std::string& filepath, std::vector<Point>& vertices,
    std::vector<Point>& normals,
    std::vector<Point2D>& textures) {

    // Determinar a extensão do ficheiro
    size_t dotIndex = filepath.find_last_of(".");
    if (dotIndex == std::string::npos) {
        std::cerr << "Erro: Extensão do ficheiro desconhecida para " << filepath << std::endl;
		return;
    }

    std::string extension = filepath.substr(dotIndex + 1);

    if (extension == "3d") {
        std::cout << "A carregar ficheiro .3d: " << filepath << std::endl;
        parse3DfileExtended(filepath, vertices, normals, textures);
    } 
    /*else if (extension == "obj") {
        std::cout << "A carregar ficheiro .obj: " << filepath << std::endl;
        points = parseOBJfile(filepath);
    } */
    else {
        std::cerr << "Erro: Formato de ficheiro não suportado para " << filepath << std::endl;
    }

}

void saveToFileExtended(const std::vector<Point>& vertices,
                        const std::vector<Point>& normals,
                        const std::vector<Point2D>& textures,
                        const std::string& filename) {
    std::string fullPath = DIR + filename;
    std::cout << "Tentando salvar o ficheiro em: " << fullPath << std::endl;
    std::ofstream file(fullPath);
    if (!file.is_open()) {
        std::cerr << "Erro ao abrir o ficheiro: " << filename << std::endl;
        return;
    }

    file << "# " << vertices.size() << std::endl;
    for (size_t i = 0; i < vertices.size(); ++i) {
        file << "p " << vertices[i].x << " " << vertices[i].y << " " << vertices[i].z << " "
             << normals[i].x << " " << normals[i].y << " " << normals[i].z << " "
             << textures[i].x << " " << textures[i].y << std::endl;
    }

    file.close();
    std::cout << "Ficheiro guardado com sucesso em: " << fullPath << std::endl;
}
