#include <iostream>
#include <math.h>
#include <random>
#include <vector>

#include "cloth.h"
#include "collision/plane.h"
#include "collision/sphere.h"

using namespace std;

Cloth::Cloth(double width, double height, int num_width_points,
             int num_height_points, float thickness) {
  this->width = width;
  this->height = height;
  this->num_width_points = num_width_points;
  this->num_height_points = num_height_points;
  this->thickness = thickness;

  buildGrid();
  buildClothMesh();
}

Cloth::~Cloth() {
  point_masses.clear();
  springs.clear();

  if (clothMesh) {
    delete clothMesh;
  }
}

Vector3D getPos(float x, float y, e_orientation orientation) {
  if (orientation == HORIZONTAL)
    return Vector3D(x, 1, y);
  else {
    float z = rand() / (500. * RAND_MAX) - 1. / 1000.;
    return Vector3D(x, y, z);
  }
}

bool isValid(int i, int j, int num_height, int num_width) {
  return i >= 0 and i < num_height and j >= 0 and j < num_width;
}

void Cloth::buildGrid() {
  // TODO (Part 1): Build a grid of masses and springs.
  float dx = width / (num_width_points - 1);
  float dy = height / (num_height_points - 1);
  for (int i = 0; i < num_height_points; i++) {
    for (int j = 0; j < num_width_points; j++) {
      Vector3D pos = getPos(j * dx, i * dy, orientation);
      PointMass m = PointMass(pos, false);
      point_masses.push_back(m);
    }
//    if (i < pinned.size())
//    for (auto j : pinned[i]) {
//      cout << j << ", " << i << endl;
//      point_masses[i * num_width_points + j].pinned = true;
//    }
  }

  for (auto p : pinned) {
    point_masses[p[1] * num_width_points + p[0]].pinned = true;
  }

  for (int i = 0; i < num_height_points; i++) {
    for (int j = 0; j < num_width_points; j++) {
      PointMass* m = &(point_masses[i * num_width_points + j]);
      if (isValid(i - 1, j, num_height_points, num_width_points)) {
        springs.emplace_back(m, &(point_masses[(i - 1) * num_width_points + j]), STRUCTURAL);
      }
      if (isValid(i, j - 1, num_height_points, num_width_points)) {
        springs.emplace_back(m, &(point_masses[i * num_width_points + j - 1]), STRUCTURAL);
      }
      if (isValid(i - 1, j - 1, num_height_points, num_width_points)) {
        springs.emplace_back(m, &(point_masses[(i - 1) * num_width_points + j - 1]), SHEARING);
      }
      if (isValid(i - 1, j + 1, num_height_points, num_width_points)) {
        springs.emplace_back(m, &(point_masses[(i - 1) * num_width_points + j + 1]), SHEARING);
      }
      if (isValid(i - 2, j, num_height_points, num_width_points)) {
        springs.emplace_back(m, &(point_masses[(i - 2) * num_width_points + j]), BENDING);
      }
      if (isValid(i, j - 2, num_height_points, num_width_points)) {
        springs.emplace_back(m, &(point_masses[i * num_width_points + j - 2]), BENDING);
      }
    }
  }
}

void Cloth::simulate(double frames_per_sec, double simulation_steps, ClothParameters *cp,
                     vector<Vector3D> external_accelerations,
                     vector<CollisionObject *> *collision_objects) {
  double mass = width * height * cp->density / num_width_points / num_height_points;
  double delta_t = 1.0f / frames_per_sec / simulation_steps;

  // TODO (Part 2): Compute total force acting on each point mass.
  for (auto& point_mass : point_masses) {
    point_mass.forces = Vector3D(0, 0, 0);
    for (const auto& a : external_accelerations) {
      point_mass.forces += a * mass;
    }
  }

  for (auto spring : springs) {
    e_spring_type type = spring.spring_type;
    if ((type == STRUCTURAL and cp->enable_structural_constraints)
    or (type == SHEARING and cp->enable_shearing_constraints)
    or (type == BENDING and cp->enable_bending_constraints)) {
      Vector3D x21 = spring.pm_b->position - spring.pm_a->position;
      double dl = x21.norm() - spring.rest_length;
      double ks = cp->ks;
      if (type == BENDING) ks *= 0.2;
      Vector3D force12 = ks * dl * x21.unit();
      spring.pm_a->forces += force12;
      spring.pm_b->forces += -force12;
    }
  }


  // TODO (Part 2): Use Verlet integration to compute new point mass positions
  for (auto& point_mass : point_masses) {
    if (point_mass.pinned) continue;
    Vector3D new_pos = point_mass.position + (1 - cp->damping / 100.) * (point_mass.position - point_mass.last_position) + point_mass.forces * delta_t * delta_t / mass;
    point_mass.last_position = point_mass.position;
    point_mass.position = new_pos;
  }

  // TODO (Part 4): Handle self-collisions.
  build_spatial_map();
  for (auto& point_mass : point_masses) {
    self_collide(point_mass, simulation_steps);
  }


  // TODO (Part 3): Handle collisions with other primitives.
  for (auto& pm : point_masses) {
    for (auto *obj : *collision_objects) {
      obj->collide(pm);
    }
  }


  // TODO (Part 2): Constrain the changes to be such that the spring does not change
  // in length more than 10% per timestep [Provot 1995].
  for(auto spring: springs) {
    PointMass *a = spring.pm_a;
    PointMass *b = spring.pm_b;
    Vector3D xb = b->position;
    Vector3D xa = a->position;
    double excess = (xb - xa).norm() - 1.1 * spring.rest_length;
    if (excess > 0) {
      if (a->pinned and b->pinned) {
        continue;
      } else if (a->pinned) {
        b->position += excess * (xa - xb).unit();
      } else if (b->pinned) {
        a->position += excess * (xb - xa).unit();
      } else {
        a->position += excess * (xb - xa).unit() / 2;
        b->position += excess * (xa - xb).unit() / 2;
      }
    }
  }

}

void Cloth::build_spatial_map() {
  for (const auto &entry : map) {
    delete(entry.second);
  }
  map.clear();

  // TODO (Part 4): Build a spatial map out of all of the point masses.
  for (auto& pm: point_masses) {
    float key = hash_position(pm.position);
    if (map.count(key) == 0) {
      map.insert({key, new vector<PointMass *>});
    }
    map[key]->push_back(&pm);
  }
}

void Cloth::self_collide(PointMass &pm, double simulation_steps) {
  // TODO (Part 4): Handle self-collision for a given point mass.
  Vector3D correction = {0, 0, 0};
  int n = 0;
  for (auto *q : *map[hash_position(pm.position)]) {
    if (q == &pm) continue;
    Vector3D dr = q->position - pm.position;
    if (dr.norm() < 2 * thickness) {
      correction += -dr.unit() * (2 * thickness - dr.norm());
    }
  }
  
//  for (auto& q : point_masses) {
//    if (&q == &pm)
//      continue;
//    Vector3D dr = q.position - pm.position;
//    if (dr.norm() < 2 * thickness) {
//      correction += -dr.unit() * (2 * thickness - dr.norm());
//      n += 1;
//    }
//  }
  if (n > 0) {
    correction /= simulation_steps * n;
    pm.position += correction;
  }
}

float Cloth::hash_position(Vector3D pos) {
  // TODO (Part 4): Hash a 3D position into a unique float identifier that represents membership in some 3D box volume.
//  float w, h, t;
//  w = 3 * width / num_width_points;
//  h = 3 * height / num_height_points;
//  t = max(w, h);
//  float a = pos.x - fmod(pos.x, w), b = pos.y - fmod(pos.y, h), c = pos.z - fmod(pos.z, t);
////  cout << (100 * a + 10 * b + c) << endl;
//  return (100 * a + 10 * b + c);
    double w = 3.0 * width / num_width_points;
    double h = 3.0 * height / num_height_points;
    double t = max(w, h);

    double x = (pos.x - fmod(pos.x, w)) / w;
    double y = (pos.y - fmod(pos.y, h)) / h;
    double z = (pos.z - fmod(pos.z, t)) / t;
    return pow(x, 5) + pow(y, 7) + pow(z, 11);
}

///////////////////////////////////////////////////////
/// YOU DO NOT NEED TO REFER TO ANY CODE BELOW THIS ///
///////////////////////////////////////////////////////

void Cloth::reset() {
  PointMass *pm = &point_masses[0];
  for (int i = 0; i < point_masses.size(); i++) {
    pm->position = pm->start_position;
    pm->last_position = pm->start_position;
    pm++;
  }
}

void Cloth::buildClothMesh() {
  if (point_masses.size() == 0) return;

  ClothMesh *clothMesh = new ClothMesh();
  vector<Triangle *> triangles;

  // Create vector of triangles
  for (int y = 0; y < num_height_points - 1; y++) {
    for (int x = 0; x < num_width_points - 1; x++) {
      PointMass *pm = &point_masses[y * num_width_points + x];
      // Get neighboring point masses:
      /*                      *
       * pm_A -------- pm_B   *
       *             /        *
       *  |         /   |     *
       *  |        /    |     *
       *  |       /     |     *
       *  |      /      |     *
       *  |     /       |     *
       *  |    /        |     *
       *      /               *
       * pm_C -------- pm_D   *
       *                      *
       */

      float u_min = x;
      u_min /= num_width_points - 1;
      float u_max = x + 1;
      u_max /= num_width_points - 1;
      float v_min = y;
      v_min /= num_height_points - 1;
      float v_max = y + 1;
      v_max /= num_height_points - 1;

      PointMass *pm_A = pm                       ;
      PointMass *pm_B = pm                    + 1;
      PointMass *pm_C = pm + num_width_points    ;
      PointMass *pm_D = pm + num_width_points + 1;

      Vector3D uv_A = Vector3D(u_min, v_min, 0);
      Vector3D uv_B = Vector3D(u_max, v_min, 0);
      Vector3D uv_C = Vector3D(u_min, v_max, 0);
      Vector3D uv_D = Vector3D(u_max, v_max, 0);


      // Both triangles defined by vertices in counter-clockwise orientation
      triangles.push_back(new Triangle(pm_A, pm_C, pm_B,
                                       uv_A, uv_C, uv_B));
      triangles.push_back(new Triangle(pm_B, pm_C, pm_D,
                                       uv_B, uv_C, uv_D));
    }
  }

  // For each triangle in row-order, create 3 edges and 3 internal halfedges
  for (int i = 0; i < triangles.size(); i++) {
    Triangle *t = triangles[i];

    // Allocate new halfedges on heap
    Halfedge *h1 = new Halfedge();
    Halfedge *h2 = new Halfedge();
    Halfedge *h3 = new Halfedge();

    // Allocate new edges on heap
    Edge *e1 = new Edge();
    Edge *e2 = new Edge();
    Edge *e3 = new Edge();

    // Assign a halfedge pointer to the triangle
    t->halfedge = h1;

    // Assign halfedge pointers to point masses
    t->pm1->halfedge = h1;
    t->pm2->halfedge = h2;
    t->pm3->halfedge = h3;

    // Update all halfedge pointers
    h1->edge = e1;
    h1->next = h2;
    h1->pm = t->pm1;
    h1->triangle = t;

    h2->edge = e2;
    h2->next = h3;
    h2->pm = t->pm2;
    h2->triangle = t;

    h3->edge = e3;
    h3->next = h1;
    h3->pm = t->pm3;
    h3->triangle = t;
  }

  // Go back through the cloth mesh and link triangles together using halfedge
  // twin pointers

  // Convenient variables for math
  int num_height_tris = (num_height_points - 1) * 2;
  int num_width_tris = (num_width_points - 1) * 2;

  bool topLeft = true;
  for (int i = 0; i < triangles.size(); i++) {
    Triangle *t = triangles[i];

    if (topLeft) {
      // Get left triangle, if it exists
      if (i % num_width_tris != 0) { // Not a left-most triangle
        Triangle *temp = triangles[i - 1];
        t->pm1->halfedge->twin = temp->pm3->halfedge;
      } else {
        t->pm1->halfedge->twin = nullptr;
      }

      // Get triangle above, if it exists
      if (i >= num_width_tris) { // Not a top-most triangle
        Triangle *temp = triangles[i - num_width_tris + 1];
        t->pm3->halfedge->twin = temp->pm2->halfedge;
      } else {
        t->pm3->halfedge->twin = nullptr;
      }

      // Get triangle to bottom right; guaranteed to exist
      Triangle *temp = triangles[i + 1];
      t->pm2->halfedge->twin = temp->pm1->halfedge;
    } else {
      // Get right triangle, if it exists
      if (i % num_width_tris != num_width_tris - 1) { // Not a right-most triangle
        Triangle *temp = triangles[i + 1];
        t->pm3->halfedge->twin = temp->pm1->halfedge;
      } else {
        t->pm3->halfedge->twin = nullptr;
      }

      // Get triangle below, if it exists
      if (i + num_width_tris - 1 < 1.0f * num_width_tris * num_height_tris / 2.0f) { // Not a bottom-most triangle
        Triangle *temp = triangles[i + num_width_tris - 1];
        t->pm2->halfedge->twin = temp->pm3->halfedge;
      } else {
        t->pm2->halfedge->twin = nullptr;
      }

      // Get triangle to top left; guaranteed to exist
      Triangle *temp = triangles[i - 1];
      t->pm1->halfedge->twin = temp->pm2->halfedge;
    }

    topLeft = !topLeft;
  }

  clothMesh->triangles = triangles;
  this->clothMesh = clothMesh;
}
