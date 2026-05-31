# Computação Gráfica
---

## Grade: 18/20 ⭐
---

## Project: Solar System Visualization
---

**Learning Outcomes**

- Develop a graphics pipeline with a generator for 3D primitives and an engine for rendering  
- Implement Bézier surfaces, vertex buffer objects (VBOs), and indexed buffer objects (IBOs)  
- Apply geometric transformations (translation, rotation, scaling) and timed animations  
- Support materials, textures, and lighting for enhanced scene realism  
- Create a dynamic visualization of the Solar System with animated orbits  

---

## Project Overview

This project, developed for the *Computação Gráfica* course at Universidade do Minho, consisted of building a 3D graphics system with two main components: a **Generator** for creating 3D primitives and an **Engine** for rendering complex scenes. The project culminated in a dynamic visualization of the Solar System, incorporating planets, orbits, and a comet, with support for animations, textures, and lighting.

Key functionalities include:  

- Generation of 3D primitives (plane, box, sphere, cone, torus, helix, Bézier patches)  
- Hierarchical scene rendering with transformations (translation, rotation, scaling)  
- Support for VBOs, IBOs, and VAOs for efficient rendering  
- Timed animations using Catmull-Rom curves for smooth motion  
- Application of materials, textures, and lighting for realistic visualization  

### Main Features:
- **Generator:** Produces 3D models (e.g., plane, sphere, Bézier patches) with vertex, normal, and texture coordinates, stored in `.3d` files  
- **Engine:** Renders hierarchical scenes from XML configurations, supporting transformations, VBOs, IBOs, materials, and lights  
- **Solar System:** Animated scene with planets orbiting the Sun, a comet following a Catmull-Rom curve, and textured models  
- **Animations:** Timed translations and rotations for dynamic object movement  
- **Testing:** Validated rendering and animations with test scenes (e.g., animated teapot, static models)  

---

## Implementation

- **Tools:** C++ with OpenGL for rendering, GLM for matrix operations, and XML parsing for scene configuration  
- **Generator:** 
  - Generates primitives (plane, box, sphere, cone, torus, helix) with calculated normals and texture coordinates  
  - Supports Bézier patches by reading `.patch` files and triangulating surfaces  
  - Outputs `.3d` files with vertex, normal, and texture data for engine compatibility  
- **Engine:** 
  - Parses XML for hierarchical scene structure (groups, models, transformations)  
  - Uses VBOs/IBOs/VAOs for efficient vertex data management  
  - Implements materials, textures, and lighting for realistic rendering  
  - Supports timed animations with Catmull-Rom curves for smooth object motion  
- **Solar System:** Combines multiple primitives with textures, lighting, and animations to simulate planetary orbits and a comet’s path  

---

## Testing & Results

- Validated primitive generation for plane, box, sphere, cone, torus, helix, and Bézier patches  
- Tested hierarchical rendering with transformations (translation, rotation, scaling)  
- Confirmed smooth animations using Catmull-Rom curves in test scenes (e.g., animated teapot)  
- Verified texture and lighting application in the Solar System scene  
- Achieved correct rendering of all models with no visual artifacts  

---

## Developed by:

[Edgar Ferreira](https://github.com/Edegare)  
[Fernando Pires](https://github.com/ferjpires)  
[Sara Silva](https://github.com/sarasilv-a)  
[Zita Duarte](https://github.com/zitamduarte)  

