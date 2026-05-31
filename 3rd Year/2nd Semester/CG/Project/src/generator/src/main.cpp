#include <iostream>
#include <string>
#include "../include/solar.hpp"
#include "../include/plane.hpp"
#include "../include/box.hpp"
#include "../include/sphere.hpp"
#include "../include/cone.hpp"
#include "../include/torus.hpp"
#include "../include/helix.hpp"
#include "../include/patch.hpp"

void printUsage() {
    std::cerr << "Uso correto:\n";
    std::cerr << "  ./generator plane <size> <divisions> <output_file>\n";
    std::cerr << "  ./generator box <length> <divisions> <output_file>\n";
    std::cerr << "  ./generator sphere <radius> <slices> <stacks> <output_file>\n";
    std::cerr << "  ./generator cone <radius> <height> <slices> <stacks> <output_file>\n";
    std::cerr << "  ./generator torus <majorRadius> <minorRadius> <sides> <rings> <output_file>\n";
    std::cerr << "  ./generator helix <radius> <height> <turns> <slices> <output_file>\n";
    std::cerr << "  ./generator solar\n";
    std::cerr << "  ./generator patch <input_file> <tesselation> <output_file>\n";
}


int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "Erro: Nenhuma primitiva especificada.\n";
        printUsage();
        return 1;
    }

    std::string primitive = argv[1];

    if (primitive == "solar") {
        saveSphere(1.0f, 20, 20, "sphere.3d");
        saveTorus(1.6f, 0.2f, 2, 15, "torus.3d");
        saveBox(1.0f, 1, "box.3d");
        saveCone(1.0f, 1.0f, 20, 5, "cone.3d");
        savePatch("comet.patch", 10, "comet.3d");
        solar_system_gen();
    }
    else if (primitive == "plane" && argc == 5) {
        float size = std::stof(argv[2]);
        int divisions = std::stoi(argv[3]);
        std::string filename = argv[4];
        savePlane(size, divisions, filename);
    } 
    else if (primitive == "box" && argc == 5) {
        float length = std::stof(argv[2]);
        int divisions = std::stoi(argv[3]);
        std::string filename = argv[4];
        saveBox(length, divisions, filename);
    } 
    else if (primitive == "sphere" && argc == 6) {
        float radius = std::stof(argv[2]);
        int slices = std::stoi(argv[3]);
        int stacks = std::stoi(argv[4]);
        std::string filename = argv[5];
        saveSphere(radius, slices, stacks, filename);
    } 
    else if (primitive == "cone" && argc == 7) {
        float radius = std::stof(argv[2]);
        float height = std::stof(argv[3]);
        int slices = std::stoi(argv[4]);
        int stacks = std::stoi(argv[5]);
        std::string filename = argv[6];
        saveCone(radius, height, slices, stacks, filename);
    } 
    else if (primitive == "torus" && argc == 7) {
        float majorRadius = std::stof(argv[2]);
        float minorRadius = std::stof(argv[3]);
        int sides = std::stoi(argv[4]);
        int rings = std::stoi(argv[5]);
        std::string filename = argv[6];
        saveTorus(majorRadius, minorRadius, sides, rings, filename);
    }
    else if (primitive == "helix" && argc == 7) {
        float radius = std::stof(argv[2]);
        float height = std::stof(argv[3]);
        int turns = std::stoi(argv[4]);
        int slices = std::stoi(argv[5]);
        std::string filename = argv[6];
        saveHelix(radius, height, turns, slices, filename);
    }    
    else if (primitive == "patch" && argc == 5) {
        std::string patch = argv[2];
        int tessel = std::stoi(argv[3]);
        std::string filename = argv[4];
        savePatch(patch, tessel, filename);
    }
    else {
        std::cerr << "Erro: Parâmetros incorretos.\n";
        printUsage();
        std::cerr << "primitive: " << primitive << " argc: " << argc << std::endl;
        return 1;
    }

    return 0;
}
