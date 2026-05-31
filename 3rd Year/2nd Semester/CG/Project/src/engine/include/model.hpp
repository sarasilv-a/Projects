#ifndef MODEL_HPP  
#define MODEL_HPP  

#include <unordered_map>
#include <vector>
#include <string>
#include <iostream>

#include <IL/il.h>

#ifdef __APPLE__  
#include <GLUT/glut.h>  
#else  
#include <GL/glew.h>  
#include <GL/glut.h>  
#endif  


#include "point.hpp"  
#include "utils.hpp"  
#include "material.hpp"  
#include "point2d.hpp"  

class Model {  
public:  
   std::string textureFile = "";  
   Material material = Material();  

   Model();  
   // Construtor atualizado  
   Model(const std::vector<Point>& vertices,  
       const std::vector<Point>& normals,  
       const std::vector<Point2D>& textures,  
       const std::string& textureFile = "",  
       const Material& mat = Material());  

   void draw(bool norm, bool light);  
   void prepareModel();  
   void initMaterial();  
   void loadTexture();
   void drawNormals(bool light);  

private:  
   std::vector<Point2D> textures;  
   std::vector<Point> vertices;  
   std::vector<unsigned int> indices;  
   std::vector<Point> normalsData;  
   GLuint vbo = 0, ebo = 0, normals = 0, textureId = 0, textureVBO = 0;;
};  

#endif // MODEL_HPP
