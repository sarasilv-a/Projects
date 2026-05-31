#define _USE_MATH_DEFINES
#include "../include/solar.hpp"



void addMaterialAndTexture(rapidxml::xml_document<>& doc,
    rapidxml::xml_node<>* modelNode,
    const std::string& texture,
    const SolarMaterial& material) {

    if (!texture.empty()) {
        rapidxml::xml_node<>* textureNode = doc.allocate_node(rapidxml::node_element, "texture");
		textureNode->append_attribute(doc.allocate_attribute("file", doc.allocate_string(texture.c_str())));
		modelNode->append_node(textureNode);
    }

    rapidxml::xml_node<>* color = doc.allocate_node(rapidxml::node_element, "color");

    // Difuso
    rapidxml::xml_node<>* diffuse = doc.allocate_node(rapidxml::node_element, "diffuse");
    diffuse->append_attribute(doc.allocate_attribute("R", doc.allocate_string(std::to_string(material.diffuse[0]).c_str())));
    diffuse->append_attribute(doc.allocate_attribute("G", doc.allocate_string(std::to_string(material.diffuse[1]).c_str())));
    diffuse->append_attribute(doc.allocate_attribute("B", doc.allocate_string(std::to_string(material.diffuse[2]).c_str())));
    color->append_node(diffuse);

    // Ambiente
    rapidxml::xml_node<>* ambient = doc.allocate_node(rapidxml::node_element, "ambient");
    ambient->append_attribute(doc.allocate_attribute("R", doc.allocate_string(std::to_string(material.ambient[0]).c_str())));
    ambient->append_attribute(doc.allocate_attribute("G", doc.allocate_string(std::to_string(material.ambient[1]).c_str())));
    ambient->append_attribute(doc.allocate_attribute("B", doc.allocate_string(std::to_string(material.ambient[2]).c_str())));
    color->append_node(ambient);

    // Especular
    rapidxml::xml_node<>* specular = doc.allocate_node(rapidxml::node_element, "specular");
    specular->append_attribute(doc.allocate_attribute("R", doc.allocate_string(std::to_string(material.specular[0]).c_str())));
    specular->append_attribute(doc.allocate_attribute("G", doc.allocate_string(std::to_string(material.specular[1]).c_str())));
    specular->append_attribute(doc.allocate_attribute("B", doc.allocate_string(std::to_string(material.specular[2]).c_str())));
    color->append_node(specular);

    // Emissivo
    rapidxml::xml_node<>* emissive = doc.allocate_node(rapidxml::node_element, "emissive");
    emissive->append_attribute(doc.allocate_attribute("R", doc.allocate_string(std::to_string(material.emissive[0]).c_str())));
    emissive->append_attribute(doc.allocate_attribute("G", doc.allocate_string(std::to_string(material.emissive[1]).c_str())));
    emissive->append_attribute(doc.allocate_attribute("B", doc.allocate_string(std::to_string(material.emissive[2]).c_str())));
    color->append_node(emissive);

    // Brilho
    rapidxml::xml_node<>* shininess = doc.allocate_node(rapidxml::node_element, "shininess");
    shininess->append_attribute(doc.allocate_attribute(
        "value", doc.allocate_string(std::to_string(material.shininess).c_str())));
    color->append_node(shininess);

    modelNode->append_node(color);
}

// Função para criar um nó de transformação
rapidxml::xml_node<>* createTransformNode(rapidxml::xml_document<> &doc, const std::vector<Transform>& transforms) {
    rapidxml::xml_node<> *transformNode = doc.allocate_node(rapidxml::node_element, "transform");

    for (const Transform& t : transforms) {
        if (t.type == "translate") {
            if (!t.curvePoints.empty() && t.time > 0) {
                rapidxml::xml_node<> *translate = doc.allocate_node(rapidxml::node_element, "translate");
                translate->append_attribute(doc.allocate_attribute("time", doc.allocate_string(std::to_string(t.time).c_str())));
                translate->append_attribute(doc.allocate_attribute("align", t.align ? "true" : "false"));

                for (const Point& pt : t.curvePoints) {
                    rapidxml::xml_node<> *pointNode = doc.allocate_node(rapidxml::node_element, "point");
                    pointNode->append_attribute(doc.allocate_attribute("x", doc.allocate_string(std::to_string(pt.x).c_str())));
                    pointNode->append_attribute(doc.allocate_attribute("y", doc.allocate_string(std::to_string(pt.y).c_str())));
                    pointNode->append_attribute(doc.allocate_attribute("z", doc.allocate_string(std::to_string(pt.z).c_str())));
                    translate->append_node(pointNode);
                }

                transformNode->append_node(translate);
            } else {
                rapidxml::xml_node<> *translate = doc.allocate_node(rapidxml::node_element, "translate");
                translate->append_attribute(doc.allocate_attribute("x", doc.allocate_string(std::to_string(t.translate[0]).c_str())));
                translate->append_attribute(doc.allocate_attribute("y", doc.allocate_string(std::to_string(t.translate[1]).c_str())));
                translate->append_attribute(doc.allocate_attribute("z", doc.allocate_string(std::to_string(t.translate[2]).c_str())));
                transformNode->append_node(translate);
            }
        } else if (t.type == "rotate") {
            rapidxml::xml_node<> *rotate = doc.allocate_node(rapidxml::node_element, "rotate");
            if (t.time > 0) {
                rotate->append_attribute(doc.allocate_attribute("time", doc.allocate_string(std::to_string(t.time).c_str())));
            } else {
                rotate->append_attribute(doc.allocate_attribute("angle", doc.allocate_string(std::to_string(t.rotate[0]).c_str())));
            }
            rotate->append_attribute(doc.allocate_attribute("x", doc.allocate_string(std::to_string(t.rotate[1]).c_str())));
            rotate->append_attribute(doc.allocate_attribute("y", doc.allocate_string(std::to_string(t.rotate[2]).c_str())));
            rotate->append_attribute(doc.allocate_attribute("z", doc.allocate_string(std::to_string(t.rotate[3]).c_str())));
            transformNode->append_node(rotate);
        } else if (t.type == "scale") {
            rapidxml::xml_node<> *scale = doc.allocate_node(rapidxml::node_element, "scale");
            scale->append_attribute(doc.allocate_attribute("x", doc.allocate_string(std::to_string(t.scale[0]).c_str())));
            scale->append_attribute(doc.allocate_attribute("y", doc.allocate_string(std::to_string(t.scale[1]).c_str())));
            scale->append_attribute(doc.allocate_attribute("z", doc.allocate_string(std::to_string(t.scale[2]).c_str())));
            transformNode->append_node(scale);
        }
    }

    return transformNode;
}


std::vector<Point> generateCircularOrbit(float radius, float angleOffsetDeg, int segments = 20) {
    std::vector<Point> points;
    if (radius<=0.0f) return points;
    float angleOffsetRad = angleOffsetDeg * static_cast<float>(M_PI) / 180.0f;
    for (int i = 0; i < segments; ++i) {
        float angle = 2.0f * static_cast<float>(M_PI) * i / static_cast<float>(segments) + angleOffsetRad;
        points.emplace_back(radius * sinf(angle), 0.0f, radius * cosf(angle));
    }
    return points;
}

void addPlanet(rapidxml::xml_document<>& doc, rapidxml::xml_node<>* parent, const PlanetData& planet) {
    rapidxml::xml_node<>* group = doc.allocate_node(rapidxml::node_element, "group");
    float angle = static_cast<float>(rand() % 360);

    std::vector<Transform> transforms;

    Transform translate;
    translate.type = "translate";
    translate.time = static_cast<float>(planet.orbitTime);
    translate.align = true;
    translate.curvePoints = generateCircularOrbit(planet.distance, angle);
    transforms.push_back(translate);

    Transform rotation;
    rotation.type = "rotate";
    rotation.time = 20;
    rotation.rotate[1] = 0;
    rotation.rotate[2] = 1;
    rotation.rotate[3] = 0;
    transforms.push_back(rotation);

    Transform scaling;
    scaling.type = "scale";
    scaling.scale[0] = planet.scale;
    scaling.scale[1] = planet.scale;
    scaling.scale[2] = planet.scale;
    transforms.push_back(scaling);

    group->append_node(createTransformNode(doc, transforms));

    rapidxml::xml_node<>* models = doc.allocate_node(rapidxml::node_element, "models");
    rapidxml::xml_node<>* model = doc.allocate_node(rapidxml::node_element, "model");
    model->append_attribute(doc.allocate_attribute("file", "sphere.3d"));
    addMaterialAndTexture(doc, model, planet.texture, planet.material);
    models->append_node(model);
    group->append_node(models);

    if (!planet.ringTexture.empty()) {

        float ring_angle = static_cast<float>(rand() % 360);
        rapidxml::xml_node<>* ringGroup = doc.allocate_node(rapidxml::node_element, "group");
        Transform t;
        t.type = "rotate";
        t.rotate[0] = ring_angle;
        t.rotate[1] = 1;
        std::vector<Transform> ringTransforms = { t };
        ringGroup->append_node(createTransformNode(doc, ringTransforms));

        rapidxml::xml_node<>* ringModels = doc.allocate_node(rapidxml::node_element, "models");
        rapidxml::xml_node<>* ringModel = doc.allocate_node(rapidxml::node_element, "model");
        ringModel->append_attribute(doc.allocate_attribute("file", "torus.3d"));
        SolarMaterial ringMat;
        ringMat.diffuse[0] = 200.0f; ringMat.diffuse[1] = 200.0f; ringMat.diffuse[2] = 200.0f;
        ringMat.ambient[0] = 50.0f; ringMat.ambient[1] = 50.0f; ringMat.ambient[2] = 50.0f;
        ringMat.specular[0] = 0.0f; ringMat.specular[1] = 0.0f; ringMat.specular[2] = 0.0f;
        ringMat.emissive[0] = 0.0f; ringMat.emissive[1] = 0.0f; ringMat.emissive[2] = 0.0f;
        ringMat.shininess = 1.0f;

        addMaterialAndTexture(doc, ringModel, planet.ringTexture, ringMat);
        ringModels->append_node(ringModel);
        ringGroup->append_node(ringModels);

        group->append_node(ringGroup);
    }

	for (const auto& moon : planet.moons) {
		rapidxml::xml_node<>* moonGroup = doc.allocate_node(rapidxml::node_element, "group");
		float moonAngle = static_cast<float>(rand() % 360);
		std::vector<Transform> moonTransforms;
		
        Transform t2;
		t2.type = "rotate";
		t2.rotate[0] = moonAngle;
		t2.rotate[2] = 1;
		moonTransforms.push_back(t2);
		
        Transform t1;
		t1.type = "translate";
		t1.translate[0] = moon.distance;
		moonTransforms.push_back(t1);
		
        Transform mSpin;
		mSpin.type = "rotate";
		mSpin.time = 50;
		mSpin.rotate[2] = 1;
		moonTransforms.push_back(mSpin);

		Transform t3;
		t3.type = "scale";
		t3.scale[0] = moon.radius;
		t3.scale[1] = moon.radius;
		t3.scale[2] = moon.radius;
		moonTransforms.push_back(t3);

		moonGroup->append_node(createTransformNode(doc, moonTransforms));
		rapidxml::xml_node<>* moonModels = doc.allocate_node(rapidxml::node_element, "models");
		rapidxml::xml_node<>* moonModel = doc.allocate_node(rapidxml::node_element, "model");
		moonModel->append_attribute(doc.allocate_attribute("file", "sphere.3d"));
        SolarMaterial moonMat;
        moonMat.diffuse[0] = 100.0f; moonMat.diffuse[1] = 100.0f; moonMat.diffuse[2] = 100.0f;
        moonMat.ambient[0] = 40.0f; moonMat.ambient[1] = 40.0f; moonMat.ambient[2] = 40.0f;
        moonMat.specular[0] = 20.0f; moonMat.specular[1] = 20.0f; moonMat.specular[2] = 20.0f;
        moonMat.emissive[0] = 0.0f; moonMat.emissive[1] = 0.0f; moonMat.emissive[2] = 0.0f;
        moonMat.shininess = 1.0f;
        addMaterialAndTexture(doc, moonModel, "moonmap1k.jpg", moonMat);
		moonModels->append_node(moonModel);
		moonGroup->append_node(moonModels);
		group->append_node(moonGroup);
	}

    parent->append_node(group);
}

void addAsteroidBelt(rapidxml::xml_document<> &doc, rapidxml::xml_node<> *parent, 
    float innerRadius, float outerRadius, int numAsteroids) {

    rapidxml::xml_node<> *beltGroup = doc.allocate_node(rapidxml::node_element, "group");

    for (int i = 0; i < numAsteroids; i++) {
        float angle = static_cast<float>(rand() % 360);
        float distance = innerRadius + static_cast<float>(rand()) / (static_cast<float>(RAND_MAX) / (outerRadius - innerRadius));
        float heightVariation = (static_cast<float>(rand() % 100) / 100.0f) * 0.5f - 0.25f;
        float size = 0.1f + static_cast<float>(rand() % 100) / 1000.0f;

        // Criar transformações individuais
        std::vector<Transform> transforms;

        Transform tInitialRotate;
        tInitialRotate.type = "rotate";
        tInitialRotate.rotate[0] = angle;
        tInitialRotate.rotate[2] = 1;
        transforms.push_back(tInitialRotate);

        Transform tOrbitRotate;
        tOrbitRotate.type = "rotate";
        tOrbitRotate.time = 100; 
        tOrbitRotate.rotate[2] = 1;
        transforms.push_back(tOrbitRotate);

        Transform tTranslate;
        tTranslate.type = "translate";
        tTranslate.translate[0] = distance;
        tTranslate.translate[1] = heightVariation;
        tTranslate.translate[2] = 0;
        transforms.push_back(tTranslate);

        Transform tSpin;
        tSpin.type = "rotate";
        tSpin.time = 50;
        tSpin.rotate[2] = 1;
        transforms.push_back(tSpin);

        Transform tScale;
        tScale.type = "scale";
        tScale.scale[0] = size;
        tScale.scale[1] = size;
        tScale.scale[2] = size;
        transforms.push_back(tScale);

        // Criar grupo do asteroide
        rapidxml::xml_node<> *asteroid = doc.allocate_node(rapidxml::node_element, "group");
        asteroid->append_node(createTransformNode(doc, transforms));

        // Escolher modelo aleatório
        rapidxml::xml_node<> *models = doc.allocate_node(rapidxml::node_element, "models");
        rapidxml::xml_node<> *model = doc.allocate_node(rapidxml::node_element, "model");

        const char* modelFile = (rand() % 2 == 0) ? "box.3d" : "cone.3d";
        model->append_attribute(doc.allocate_attribute("file", modelFile));
        SolarMaterial asteroidMat;
        asteroidMat.diffuse[0] = 120.0f; asteroidMat.diffuse[1] = 120.0f; asteroidMat.diffuse[2] = 120.0f;
        asteroidMat.ambient[0] = 30.0f; asteroidMat.ambient[1] = 30.0f; asteroidMat.ambient[2] = 30.0f;
        asteroidMat.specular[0] = 50.0f; asteroidMat.specular[1] = 50.0f; asteroidMat.specular[2] = 50.0f;
        asteroidMat.emissive[0] = 0.0f; asteroidMat.emissive[1] = 0.0f; asteroidMat.emissive[2] = 0.0f;
        asteroidMat.shininess = 5.0f;
        addMaterialAndTexture(doc, model, "phobosbump.jpg", asteroidMat);
        models->append_node(model);

        asteroid->append_node(models);
        beltGroup->append_node(asteroid);
    }

    parent->append_node(beltGroup);
}
 
void addComet(rapidxml::xml_document<> &doc,  rapidxml::xml_node<> *parent){
    rapidxml::xml_node<> *cometGroup = doc.allocate_node(rapidxml::node_element, "group");

    std::vector<Transform> transforms;

    Transform tOrbitRotate;
    tOrbitRotate.type = "rotate";
    tOrbitRotate.time = 150; 
    tOrbitRotate.rotate[2] = 1;
    transforms.push_back(tOrbitRotate);

    Transform tTranslate;
    tTranslate.type = "translate";
    tTranslate.time = 80;
    tTranslate.align = true;
    tTranslate.curvePoints = {
        Point(26, 0, 0),
        Point(20, 5, 10),
        Point(13, 0, 0),
        Point(20, -5, -10)
    };
    transforms.push_back(tTranslate);

    Transform tSpin;
    tSpin.type = "rotate";
    tSpin.time = 60;
    tSpin.rotate[2] = 1;
    transforms.push_back(tSpin);

    Transform tScale;
    tScale.type = "scale";
    tScale.scale[0] = 0.2f;
    tScale.scale[1] = 0.2f;
    tScale.scale[2] = 0.2f;
    transforms.push_back(tScale);

    cometGroup->append_node(createTransformNode(doc, transforms));

    rapidxml::xml_node<> *models = doc.allocate_node(rapidxml::node_element, "models");
    rapidxml::xml_node<> *model = doc.allocate_node(rapidxml::node_element, "model");
    model->append_attribute(doc.allocate_attribute("file", "comet.3d"));
    SolarMaterial asteroidMat;
    asteroidMat.diffuse[0] = 120.0f; asteroidMat.diffuse[1] = 120.0f; asteroidMat.diffuse[2] = 120.0f;
    asteroidMat.ambient[0] = 30.0f; asteroidMat.ambient[1] = 30.0f; asteroidMat.ambient[2] = 30.0f;
    asteroidMat.specular[0] = 50.0f; asteroidMat.specular[1] = 50.0f; asteroidMat.specular[2] = 50.0f;
    asteroidMat.emissive[0] = 0.0f; asteroidMat.emissive[1] = 0.0f; asteroidMat.emissive[2] = 0.0f;
    asteroidMat.shininess = 5.0f;
    addMaterialAndTexture(doc, model, "phobosbump.jpg", asteroidMat);
    models->append_node(model);
    cometGroup->append_node(models);

    parent->append_node(cometGroup);
}

// Função para criar a configuração da janela
rapidxml::xml_node<>* createWindowNode(rapidxml::xml_document<> &doc) {
    rapidxml::xml_node<> *window = doc.allocate_node(rapidxml::node_element, "window");
    window->append_attribute(doc.allocate_attribute("width", "1080"));
    window->append_attribute(doc.allocate_attribute("height", "720"));
    return window;
}

// Função para criar a configuração da câmera
rapidxml::xml_node<>* createCameraNode(rapidxml::xml_document<> &doc) {
    rapidxml::xml_node<> *camera = doc.allocate_node(rapidxml::node_element, "camera");

    rapidxml::xml_node<> *position = doc.allocate_node(rapidxml::node_element, "position");
    position->append_attribute(doc.allocate_attribute("x", "10"));
    position->append_attribute(doc.allocate_attribute("y", "10"));
    position->append_attribute(doc.allocate_attribute("z", "10"));
    camera->append_node(position);

    rapidxml::xml_node<> *lookAt = doc.allocate_node(rapidxml::node_element, "lookAt");
    lookAt->append_attribute(doc.allocate_attribute("x", "0"));
    lookAt->append_attribute(doc.allocate_attribute("y", "0"));
    lookAt->append_attribute(doc.allocate_attribute("z", "0"));
    camera->append_node(lookAt);

    rapidxml::xml_node<> *up = doc.allocate_node(rapidxml::node_element, "up");
    up->append_attribute(doc.allocate_attribute("x", "0"));
    up->append_attribute(doc.allocate_attribute("y", "1"));
    up->append_attribute(doc.allocate_attribute("z", "0"));
    camera->append_node(up);

    rapidxml::xml_node<> *projection = doc.allocate_node(rapidxml::node_element, "projection");
    projection->append_attribute(doc.allocate_attribute("fov", "60"));
    projection->append_attribute(doc.allocate_attribute("near", "1"));
    projection->append_attribute(doc.allocate_attribute("far", "1000"));
    camera->append_node(projection);

    return camera;
}



// Função principal para gerar o XML do sistema solar
void solar_system_gen() {
   
    rapidxml::xml_document<> doc;
    rapidxml::xml_node<> *world = doc.allocate_node(rapidxml::node_element, "world");
    doc.append_node(world);

    world->append_node(createWindowNode(doc));
    world->append_node(createCameraNode(doc));
	
    rapidxml::xml_node<>* lights = doc.allocate_node(rapidxml::node_element, "lights");
    rapidxml::xml_node<>* light = doc.allocate_node(rapidxml::node_element, "light");
    light->append_attribute(doc.allocate_attribute("type", "point"));
    light->append_attribute(doc.allocate_attribute("posx", "0"));
    light->append_attribute(doc.allocate_attribute("posy", "0"));
    light->append_attribute(doc.allocate_attribute("posz", "0"));
    lights->append_node(light);
    world->append_node(lights);


    rapidxml::xml_node<> *root = doc.allocate_node(rapidxml::node_element, "group");
    world->append_node(root);

    // Agrupamento lógico dos planetas
    std::vector<PlanetData> innerPlanets = {
        {0.0f, 3.0f, 0, {}, "", "sunmap.jpg",
            { {255, 255, 200},  
              {100, 100, 50},   
              {0, 0, 0},        
              {255, 255, 200},  
              100.0f            
            }
        },                  // Sol
        {4.0f, 0.3f, 40, {}, "", "mercurymap.jpg"},            // Mercúrio
        {7.0f, 0.5f, 45, {}, "", "venusmap.jpg"},               // Vênus
        {10.0f, 0.5f, 50, {{1.7f, 0.4f}}, "", "earth.jpg"},      // Terra
        {14.0f, 0.4f, 55, {{1.4f, 0.2f}, {2.0f, 0.1f}}, "", "mars_1k_color.jpg"} // Marte
    };

    std::vector<PlanetData> outerPlanets = {
        {25.0f, 1.2f, 60, {{1.4f, 0.15f}, {2.0f, 0.1f}, {2.5f, 0.2f}, {3.0f, 0.25f}}, "", "jupitermap.jpg"}, // JúpITER
        {30.0f, 1.1f, 65, {{2.0f, 0.25f}}, "saturnringcolor.jpg", "saturnmap.jpg"}, // saturno
		{34.0f, 0.9f, 70, {}, "", "uranusmap.jpg"}, // urano
		{38.0f, 0.8f, 75, {}, "", "neptunemap.jpg"}, // netuno
		{42.0f, 0.6f, 80, {}, "", "plutomap1k.jpg"} // plutão
    };



    for (const auto& p : innerPlanets) {

        addPlanet(doc, root, p);
    }


    addAsteroidBelt(doc, root, 15.5f, 18.5f, 200);


    for (const auto& p : outerPlanets) {

        addPlanet(doc, root, p);
    }

 
    addComet(doc, root);

    // Salvar arquivo XML
    std::ofstream file("../src/scenes/our_tests/solar_system.xml");
    if (!file.is_open()) {
        std::cerr << "Erro: não foi possível abrir o ficheiro de saída!" << std::endl;
        return;
    }
    file << doc;
    file.close();
    doc.clear();
}
