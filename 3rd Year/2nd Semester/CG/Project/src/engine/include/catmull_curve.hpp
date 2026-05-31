#ifndef CATMULL_CURVE_HPP
#define CATMULL_CURVE_HPP

#include <math.h>
#include <vector>
#include "point.hpp"
#include "utils.hpp"

void getGlobalCatmullRomPoint(float gt, const std::vector<Point>& points, float *pos, float *deriv);



#endif // CATMULL_CURVE_HPP
