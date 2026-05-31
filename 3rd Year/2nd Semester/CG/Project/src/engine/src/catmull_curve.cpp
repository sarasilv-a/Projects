#include "catmull_curve.hpp"


void getCatmullRomPoint(float t, Point p0, Point p1, Point p2, Point p3, float *pos, float *deriv) {
    float M[4][4] = {
        {-0.5f,  1.5f, -1.5f,  0.5f},
        { 1.0f, -2.5f,  2.0f, -0.5f},
        {-0.5f,  0.0f,  0.5f,  0.0f},
        { 0.0f,  1.0f,  0.0f,  0.0f}
    };

    float T[4] = {t*t*t, t*t, t, 1};
    float Tderiv[4] = {3*t*t, 2*t, 1, 0};

    float px[4] = {p0.x, p1.x, p2.x, p3.x};
    float py[4] = {p0.y, p1.y, p2.y, p3.y};
    float pz[4] = {p0.z, p1.z, p2.z, p3.z};

    float ax[4], ay[4], az[4];
    multMatrixVector(M, px, ax);
    multMatrixVector(M, py, ay);
    multMatrixVector(M, pz, az);

    pos[0] = T[0]*ax[0] + T[1]*ax[1] + T[2]*ax[2] + T[3]*ax[3];
    pos[1] = T[0]*ay[0] + T[1]*ay[1] + T[2]*ay[2] + T[3]*ay[3];
    pos[2] = T[0]*az[0] + T[1]*az[1] + T[2]*az[2] + T[3]*az[3];

    deriv[0] = Tderiv[0]*ax[0] + Tderiv[1]*ax[1] + Tderiv[2]*ax[2] + Tderiv[3]*ax[3];
    deriv[1] = Tderiv[0]*ay[0] + Tderiv[1]*ay[1] + Tderiv[2]*ay[2] + Tderiv[3]*ay[3];
    deriv[2] = Tderiv[0]*az[0] + Tderiv[1]*az[1] + Tderiv[2]*az[2] + Tderiv[3]*az[3];

    normalize(deriv);
}

void getGlobalCatmullRomPoint(float gt, const std::vector<Point>& points, float *pos, float *deriv) {
    int n = points.size();
    float t = gt * n;
    int index = static_cast<int>(floor(t));
    t = t - index;

    int indices[4]; 
	indices[0] = (index + n-1)%n;	
	indices[1] = (indices[0]+1)%n;
	indices[2] = (indices[1]+1)%n; 
	indices[3] = (indices[2]+1)%n;

    Point p0 = points[indices[0]];
    Point p1 = points[indices[1]];
    Point p2 = points[indices[2]];
    Point p3 = points[indices[3]];

    getCatmullRomPoint(t, p0, p1, p2, p3, pos, deriv);
}

