#ifndef UTILS_HPP
#define UTILS_HPP

#include <math.h>

void buildRotMatrix(float* x, float* y, float* z, float* m);

void cross(float* a, float* b, float* res);

void normalize(float* a);

float length(float* v);

void multMatrixVector(float m[4][4], float* v, float* res);

void computeNormal(float* a, float* b, float* c, float* res);

#endif // UTILS_HPP