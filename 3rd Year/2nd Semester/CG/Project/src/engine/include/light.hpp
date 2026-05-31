#ifndef LIGHT_HPP
#define LIGHT_HPP


enum LType { D, P, S, E};

struct Light {
	LType type = E;
    float pos[4] = { 0, 0, 0, 1 };
    float dir[4] = { 0, 0, 0, 0 };
    float cut = 180;
};

#endif // LIGHT_HPP