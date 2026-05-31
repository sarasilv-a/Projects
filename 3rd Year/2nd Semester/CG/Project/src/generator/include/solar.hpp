#ifndef SOLAR_HPP
#define SOLAR_HPP

#include "../../../libs/rapidxml/rapidxml_print.hpp"
#include "../../../libs/rapidxml/rapidxml.hpp"
#include "transform.hpp"
#include "point.hpp"
#include <fstream>
#include <vector>
#include <utility> 
#include <cstdlib> 
#include <iostream>
#include <sstream> 
#include <fstream>
#include <math.h>
#include <string>
#include <cmath>

struct SolarMaterial {
    float diffuse[3] = {200.0f, 200.0f, 200.0f};
    float ambient[3] = {50.0f, 50.0f, 50.0f};
    float specular[3] = {0.0f, 0.0f, 0.0f};
    float emissive[3] = {0.0f, 0.0f, 0.0f};
    float shininess = 0.0f;
};

struct Moon {
    float distance;
    float radius;
};

struct PlanetData {
    float distance;
    float scale;
    int orbitTime;
    std::vector<Moon> moons;
    std::string ringTexture;
    std::string texture;     
	SolarMaterial material; 
};

void solar_system_gen();

#endif
