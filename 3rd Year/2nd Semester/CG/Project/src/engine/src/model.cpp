#include "model.hpp"


Model::Model() {}

Model::Model(const std::vector<Point>& points, const std::vector<Point>& normals,
    const std::vector<Point2D>& textures, const std::string& texture, const Material& mat) {
	this->vertices = points;
    this->normalsData = normals;
	this->textures = textures;
	this->textureFile = texture;
	this->material = mat;
}


void Model::draw(bool norm, bool light) {
    if (light) {
        glEnable(GL_LIGHTING);
        initMaterial();
    }

    // Vértices
    glBindBuffer(GL_ARRAY_BUFFER, vbo);
    glEnableClientState(GL_VERTEX_ARRAY);
    glVertexPointer(3, GL_FLOAT, sizeof(Point), (void*)0);

    // Normais
    glBindBuffer(GL_ARRAY_BUFFER, normals);
    glEnableClientState(GL_NORMAL_ARRAY);
    glNormalPointer(GL_FLOAT, sizeof(Point), (void*)0);

    // textures
    if (textureId) {
        glEnable(GL_TEXTURE_2D);
        glEnableClientState(GL_TEXTURE_COORD_ARRAY);

        glBindTexture(GL_TEXTURE_2D, textureId);
        glBindBuffer(GL_ARRAY_BUFFER, textureVBO);
        glTexCoordPointer(2, GL_FLOAT, 0, 0);
    }

    // Índices
    glColor3f(1.0, 1.0, 1.0);
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo);
    glDrawElements(GL_TRIANGLES, indices.size(), GL_UNSIGNED_INT, 0);

    // Desativar states
    if (textureId) {
        glDisableClientState(GL_TEXTURE_COORD_ARRAY);
        glBindTexture(GL_TEXTURE_2D, 0);
    }
    glDisableClientState(GL_VERTEX_ARRAY);
    glDisableClientState(GL_NORMAL_ARRAY);

    glBindBuffer(GL_ARRAY_BUFFER, 0);
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0);

	if (norm) {
		drawNormals(light);
	}
}

void Model::initMaterial() {
    glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, this->material.ambient);
    glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, this->material.diffuse);
    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, this->material.specular);
    glMaterialfv(GL_FRONT_AND_BACK, GL_EMISSION, this->material.emission);
    glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, this->material.shininess);
}

void Model::loadTexture() {
    if (textureFile.empty())
        return;

    unsigned int imageId;
    ilGenImages(1, &imageId);
    ilBindImage(imageId);

    std::string fullPath = "textures/" + textureFile;
    if (!ilLoadImage((ILstring)fullPath.c_str())) {
        std::cerr << "Erro ao carregar textura: " << fullPath << std::endl;
        ilDeleteImages(1, &imageId);
        return;
    }


    ilConvertImage(IL_RGBA, IL_UNSIGNED_BYTE);
    int width = ilGetInteger(IL_IMAGE_WIDTH);
    int height = ilGetInteger(IL_IMAGE_HEIGHT);
    unsigned char* texData = ilGetData();

    glGenTextures(1, &textureId);
    glBindTexture(GL_TEXTURE_2D, textureId);

    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT);

	glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
    // glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR); // MIPMAP
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);

    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0,
        GL_RGBA, GL_UNSIGNED_BYTE, texData);

    glGenerateMipmap(GL_TEXTURE_2D);

    glBindTexture(GL_TEXTURE_2D, 0);
    ilDeleteImages(1, &imageId);

}

void Model::prepareModel() {

    std::unordered_map<std::string, unsigned int> vertexMap;
    std::vector<Point> uniqueVertices;
    std::vector<Point> uniqueNormals;
	std::vector<Point2D> uniqueTextures;
    for (size_t i = 0; i < vertices.size(); i++) { // retirar todos os duplicados (vertices + normais iguais) e criar indices
        const Point& v = vertices[i];
        const Point& n = normalsData[i];
		const Point2D& t = textures[i];

        std::string key = std::to_string(v.x) + "," + std::to_string(v.y) + "," + std::to_string(v.z) +
            "|" + std::to_string(n.x) + "," + std::to_string(n.y) + "," + std::to_string(n.z) + 
            "|" + std::to_string(t.x) + "," + std::to_string(t.y);

        auto it = vertexMap.find(key);
        if (it == vertexMap.end()) { // se não existir igual
            unsigned int newIndex = uniqueVertices.size();
            vertexMap[key] = newIndex;
            uniqueVertices.push_back(v);
            uniqueNormals.push_back(n);
			uniqueTextures.push_back(t);

            indices.push_back(newIndex);
        }
        else {
            // já existe
            indices.push_back(it->second);
        }
    }

    this->vertices = uniqueVertices;
    this->normalsData = uniqueNormals;
    this->textures = uniqueTextures;

    // buffs
    glGenBuffers(1, &vbo);
    glGenBuffers(1, &normals);
    glGenBuffers(1, &textureVBO);
    glGenBuffers(1, &ebo);

    // vert
    glBindBuffer(GL_ARRAY_BUFFER, vbo);
    glBufferData(GL_ARRAY_BUFFER, vertices.size() * sizeof(Point), vertices.data(), GL_STATIC_DRAW);

    // norms
    glBindBuffer(GL_ARRAY_BUFFER, normals);
    glBufferData(GL_ARRAY_BUFFER, normalsData.size() * sizeof(Point), normalsData.data(), GL_STATIC_DRAW);

	// textures
    glBindBuffer(GL_ARRAY_BUFFER, textureVBO);
    glBufferData(GL_ARRAY_BUFFER, textures.size() * sizeof(Point2D), textures.data(), GL_STATIC_DRAW);

    // inds
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo);
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.size() * sizeof(unsigned int), indices.data(), GL_STATIC_DRAW);

    // unbind
    glBindBuffer(GL_ARRAY_BUFFER, 0);
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0);

    if (this->textureFile != "") {
         loadTexture();
    }
}

void Model::drawNormals( bool light) {
	if (light) {
		glDisable(GL_LIGHTING);
	}
    glColor3f(1.0f, 0.0f, 0.0f); 

    glBegin(GL_LINES);
    for (size_t i = 0; i < vertices.size(); ++i) {
        const Point& v = vertices[i];
        const Point& n = normalsData[i];

        glVertex3f(v.x, v.y, v.z);

        float scale = 0.2f; 
        glVertex3f(v.x + n.x * scale, v.y + n.y * scale, v.z + n.z * scale);
    }
    glEnd();

	if (light) {
		glEnable(GL_LIGHTING);
	}
}