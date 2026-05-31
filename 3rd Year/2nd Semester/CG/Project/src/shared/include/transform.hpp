#ifndef TRANSFORM_HPP
#define TRANSFORM_HPP

#include <string>
#include <vector>
#include "point.hpp"

class Transform {
    public:
        std::string type;
    
        float translate[3] = {0, 0, 0};
        float scale[3] = {1, 1, 1};
        float rotate[4] = {0, 0, 0, 0};
    
        float time = 0;
        bool align = false;
        std::vector<Point> curvePoints;
    
        Transform() {}
    };

#endif 