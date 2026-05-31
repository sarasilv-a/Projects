#include "group.hpp"
#include <ostream>
#include <iostream>

Group::Group() {}

void Group::addTransform(const Transform& transform) {
    transforms.push_back(transform);
}

void Group::addModel(const Model& model) {
    models.push_back(model);
}

void Group::addChild(const Group& child) {
    children.push_back(child);
}

void Group::draw(bool catmull, bool norm, bool light) {
    glPushMatrix();

    for (const Transform& transform : transforms) {
        // --- Translação com tempo (Catmull)---
        if (transform.curvePoints.size() >= 4 && transform.time > 0) {
			if (catmull) {
                if (light) {
                    glDisable(GL_LIGHTING);
                }
				glColor3f(1.0f, 1.0f, 1.0f);
				glBegin(GL_LINE_LOOP);
				for (float tt = 0; tt < 1; tt += 0.01f) {
					float p[3], d[3];
					getGlobalCatmullRomPoint(tt, transform.curvePoints, p, d);
					glVertex3f(p[0], p[1], p[2]);
				}
				glEnd();
                if (light) {
                    glEnable(GL_LIGHTING);
                }
			}


            float pos[3], deriv[3];

            // Tempo normalizado [0,1] baseado no tempo real e no tempo da transformação
            float elapsed = glutGet(GLUT_ELAPSED_TIME) / 1000.0f;
            float t = fmod(elapsed, transform.time) / transform.time;
            getGlobalCatmullRomPoint(t, transform.curvePoints, pos, deriv);

            glTranslatef(pos[0], pos[1], pos[2]);

            if (transform.align) {

                float up[3] = {0, 1, 0};
                float right[3];

                cross(deriv, up, right);
                normalize(right);

                cross(right, deriv, up);
                normalize(up);

                float m[16];
                buildRotMatrix(deriv, up, right, m);
                glMultMatrixf(m);
            }
        }

        // --- Rotação com tempo ---
        else if (transform.rotate[0] == 0 && transform.time != 0) {
            int dir=1;
            if (transform.time < 0) {
                dir = -1;
            }
            float elapsed = glutGet(GLUT_ELAPSED_TIME) / 1000.0f;
            float angle = fmod((elapsed / abs(transform.time)) * 360.0f, 360.0f);
            glRotatef(dir*angle, transform.rotate[1], transform.rotate[2], transform.rotate[3]);
        }

        // --- Transformações estáticas ---
        else {
            // --- Translação ---
            glTranslatef(transform.translate[0], transform.translate[1], transform.translate[2]);
            // --- Rotação ---
            glRotatef(transform.rotate[0], transform.rotate[1], transform.rotate[2], transform.rotate[3]);
            // --- Escala ---
            glScalef(transform.scale[0], transform.scale[1], transform.scale[2]);
        }
    }

    // Desenhar modelos
    for (Model& model : models)
        model.draw(norm, light);

    // Desenhar filhos
    for (Group& child : children)
        child.draw(catmull,norm,light);

    glPopMatrix();
}

void Group::prepareModels() {
    for (Model& model : models) {
        model.prepareModel();
    }
    for (Group& child : children) {
        child.prepareModels();
    }
}
