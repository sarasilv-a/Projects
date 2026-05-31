#include "parse.hpp"
#include <fstream>
#include <iostream>

#define MODELS "../src/models/"

// Parse transformações
void parseTransform(rapidxml::xml_node<>* transformNode, Group& group) {
    for (rapidxml::xml_node<>* node = transformNode->first_node(); node; node = node->next_sibling()) {
        std::string type = node->name();
        Transform transform;
        transform.type = type;

        if (type == "translate") {
            auto timeAttr = node->first_attribute("time");
            if (timeAttr) {
                transform.time = std::stof(timeAttr->value());

                auto alignAttr = node->first_attribute("align");
                transform.align = alignAttr && std::string(alignAttr->value()) == "true";

                for (rapidxml::xml_node<>* point = node->first_node("point"); point; point = point->next_sibling("point")) {
                    float x = std::stof(point->first_attribute("x")->value());
                    float y = std::stof(point->first_attribute("y")->value());
                    float z = std::stof(point->first_attribute("z")->value());
                    transform.curvePoints.emplace_back(x, y, z);
                }
            } else {
                transform.translate[0] = std::stof(node->first_attribute("x")->value());
                transform.translate[1] = std::stof(node->first_attribute("y")->value());
                transform.translate[2] = std::stof(node->first_attribute("z")->value());
            }
        }

        else if (type == "rotate") {
            auto timeAttr = node->first_attribute("time");
            if (timeAttr!=0) {
                transform.time = std::stof(timeAttr->value());
            } else {
                transform.rotate[0] = std::stof(node->first_attribute("angle")->value());
            }

            transform.rotate[1] = std::stof(node->first_attribute("x")->value());
            transform.rotate[2] = std::stof(node->first_attribute("y")->value());
            transform.rotate[3] = std::stof(node->first_attribute("z")->value());
        }

        else if (type == "scale") {
            transform.scale[0] = std::stof(node->first_attribute("x")->value());
            transform.scale[1] = std::stof(node->first_attribute("y")->value());
            transform.scale[2] = std::stof(node->first_attribute("z")->value());
        }

        group.addTransform(transform);
    }
}


// Parse de grupo
Group parseGroup(rapidxml::xml_node<>* groupNode) {
    Group group;
    
    // Transformações
    rapidxml::xml_node<>* transformNode = groupNode->first_node("transform");
    if (transformNode) {
        parseTransform(transformNode, group);
    }
    
    // Modelos
    rapidxml::xml_node<>* modelsNode = groupNode->first_node("models");
    if (modelsNode) {
        for (rapidxml::xml_node<>* modelNode = modelsNode->first_node("model"); modelNode; modelNode = modelNode->next_sibling("model")) {
            std::string filename = modelNode->first_attribute("file")->value();
            std::string filepath = MODELS + filename;

            std::string texture = "";
            Material material = Material();

            rapidxml::xml_node<>* texNode = modelNode->first_node("texture");
            if (texNode) {
                texture = texNode->first_attribute("file")->value();
            }

            rapidxml::xml_node<>* colorNode = modelNode->first_node("color");
            if (colorNode) {
				for (rapidxml::xml_node<>* node = colorNode->first_node(); node; node = node->next_sibling()) {
					std::string type = node->name();
                    if (type == "ambient") {
                        material.ambient[0] = std::stof(node->first_attribute("R")->value())/ 255.0f;
                        material.ambient[1] = std::stof(node->first_attribute("G")->value())/ 255.0f;
                        material.ambient[2] = std::stof(node->first_attribute("B")->value()) / 255.0f;
                    }
                    else if (type == "diffuse") {
                        material.diffuse[0] = std::stof(node->first_attribute("R")->value()) / 255.0f;
                        material.diffuse[1] = std::stof(node->first_attribute("G")->value()) / 255.0f;
                        material.diffuse[2] = std::stof(node->first_attribute("B")->value()) / 255.0f;
                    }
                    else if (type == "specular") {
                        material.specular[0] = std::stof(node->first_attribute("R")->value()) / 255.0f;
                        material.specular[1] = std::stof(node->first_attribute("G")->value()) / 255.0f;
                        material.specular[2] = std::stof(node->first_attribute("B")->value()) / 255.0f;
                    }
                    else if (type == "emissive") {
                        material.emission[0] = std::stof(node->first_attribute("R")->value()) / 255.0f;
                        material.emission[1] = std::stof(node->first_attribute("G")->value()) / 255.0f;
                        material.emission[2] = std::stof(node->first_attribute("B")->value()) / 255.0f;
                    }
                    else if (type == "shininess") {
                        material.shininess = std::stof(node->first_attribute("value")->value());
                    }
				}
            }
			std::vector<Point> normals;
			std::vector<Point2D> textures;
			std::vector<Point> points;
			parseFile(filepath, points, normals, textures);
            group.addModel(Model(points, normals, textures, texture, material));
        }
    }
    
    // Filhos
    for (rapidxml::xml_node<>* childGroupNode = groupNode->first_node("group"); childGroupNode; childGroupNode = childGroupNode->next_sibling("group")) {
        group.children.push_back(parseGroup(childGroupNode));
    }
    
    return group;
}

// Parse geral
Configuration parseConfig(std::string filename) {
    std::ifstream file(filename);
    if (!file.is_open()) {
        std::cerr << "Erro ao abrir o ficheiro XML: " << filename << std::endl;
        return Configuration();
    }

    std::string xmlContent((std::istreambuf_iterator<char>(file)), std::istreambuf_iterator<char>());
    file.close();

    rapidxml::xml_document<> doc;
    doc.parse<0>(&xmlContent[0]);

    rapidxml::xml_node<>* root = doc.first_node("world");

    // Janela
    Window window_info(
        std::stoi(root->first_node("window")->first_attribute("width")->value()),
        std::stoi(root->first_node("window")->first_attribute("height")->value())
    );

    // Câmera
    rapidxml::xml_node<>* cameraNode = root->first_node("camera");
    Camera camera_info(
        Point(
            std::stof(cameraNode->first_node("position")->first_attribute("x")->value()),
            std::stof(cameraNode->first_node("position")->first_attribute("y")->value()),
            std::stof(cameraNode->first_node("position")->first_attribute("z")->value())
        ),
        Point(
            std::stof(cameraNode->first_node("lookAt")->first_attribute("x")->value()),
            std::stof(cameraNode->first_node("lookAt")->first_attribute("y")->value()),
            std::stof(cameraNode->first_node("lookAt")->first_attribute("z")->value())
        ),
        Point(
            std::stof(cameraNode->first_node("up")->first_attribute("x")->value()),
            std::stof(cameraNode->first_node("up")->first_attribute("y")->value()),
            std::stof(cameraNode->first_node("up")->first_attribute("z")->value())
        ),
        std::stoi(cameraNode->first_node("projection")->first_attribute("fov")->value()),
        std::stof(cameraNode->first_node("projection")->first_attribute("near")->value()),
        std::stof(cameraNode->first_node("projection")->first_attribute("far")->value())
    );

    // Luzes
    std::vector<Light> lights = {};

    rapidxml::xml_node<>* lightsNode = root->first_node("lights");
    if (lightsNode) {
        for (rapidxml::xml_node<>* lightNode = lightsNode->first_node("light"); lightNode; lightNode = lightNode->next_sibling("light")) {
            std::string typeStr = lightNode->first_attribute("type")->value();
            
            Light light = Light();

            if (typeStr == "directional") {
                light.type = LType::D;
                light.dir[0] = std::stof(lightNode->first_attribute("dirx")->value());
                light.dir[1] = std::stof(lightNode->first_attribute("diry")->value());
                light.dir[2] = std::stof(lightNode->first_attribute("dirz")->value());
            }
            else if (typeStr == "point") {
                light.type = LType::P;
                light.pos[0] = std::stof(lightNode->first_attribute("posx")->value());
                light.pos[1] = std::stof(lightNode->first_attribute("posy")->value());
                light.pos[2] = std::stof(lightNode->first_attribute("posz")->value());
            }

            else if (typeStr == "spot") {
                light.type = LType::S;
                light.pos[0] = std::stof(lightNode->first_attribute("posx")->value());
                light.pos[1] = std::stof(lightNode->first_attribute("posy")->value());
                light.pos[2] = std::stof(lightNode->first_attribute("posz")->value());

                light.dir[0] = std::stof(lightNode->first_attribute("dirx")->value());
                light.dir[1] = std::stof(lightNode->first_attribute("diry")->value());
                light.dir[2] = std::stof(lightNode->first_attribute("dirz")->value());

                light.cut = std::stof(lightNode->first_attribute("cutoff")->value());
            }
			else continue;

            lights.push_back(light);
        }
    }

    // Grupo raiz
    Group rootGroup;
    for (rapidxml::xml_node<>* groupNode = root->first_node("group"); groupNode; groupNode = groupNode->next_sibling("group")) {
        rootGroup.children.push_back(parseGroup(groupNode));
    }

    return Configuration(window_info, camera_info, rootGroup, lights);
}