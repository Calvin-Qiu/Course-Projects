#include "bvh.h"

#include "CGL/CGL.h"
#include "triangle.h"

#include <iostream>
#include <stack>

using namespace std;

namespace CGL {
namespace SceneObjects {

BVHAccel::BVHAccel(const std::vector<Primitive *> &_primitives,
                   size_t max_leaf_size) {

  primitives = std::vector<Primitive *>(_primitives);
  root = construct_bvh(primitives.begin(), primitives.end(), max_leaf_size);
}

BVHAccel::~BVHAccel() {
  if (root)
    delete root;
  primitives.clear();
}

BBox BVHAccel::get_bbox() const { return root->bb; }

void BVHAccel::draw(BVHNode *node, const Color &c, float alpha) const {
  if (node->isLeaf()) {
    for (auto p = node->start; p != node->end; p++) {
      (*p)->draw(c, alpha);
    }
  } else {
    draw(node->l, c, alpha);
    draw(node->r, c, alpha);
  }
}

void BVHAccel::drawOutline(BVHNode *node, const Color &c, float alpha) const {
  if (node->isLeaf()) {
    for (auto p = node->start; p != node->end; p++) {
      (*p)->drawOutline(c, alpha);
    }
  } else {
    drawOutline(node->l, c, alpha);
    drawOutline(node->r, c, alpha);
  }
}

BVHNode *BVHAccel::construct_bvh(std::vector<Primitive *>::iterator start,
                                 std::vector<Primitive *>::iterator end,
                                 size_t max_leaf_size) {

  // TODO (Part 2.1):
  // Construct a BVH from the given vector of primitives and maximum leaf
  // size configuration. The starter code build a BVH aggregate with a
  // single leaf node (which is also the root) that encloses all the
  // primitives.

  BBox bbox;

  for (auto p = start; p != end; p++) {
    BBox bb = (*p)->get_bbox();
    bbox.expand(bb);
  }
  BVHNode *node = new BVHNode(bbox);
  int n = end - start;
  if (n <= max_leaf_size) {
    for (auto p = start; p != end; p++) {
      node->primitives.push_back(*p);
    }
    node->start = node->primitives.begin();
    node->end = node->primitives.end();
    return node;
  }
  Vector3D extent = bbox.extent;
  int axis = max({0, 1, 2}, [extent](const int x, const int y) {return extent[x] < extent[y];});
//  double split = 0;
//  for (auto p = start; p != end; p++) {
//    split += (*p)->get_bbox().centroid()[axis];
//  }
//  split /= n;
	double split = bbox.min[axis] + extent[axis] / 2;
  std::vector<Primitive*> left_list, right_list;
  std::sort(start, end, [axis](Primitive *x, Primitive *y) {return x->get_bbox().centroid()[axis] < y->get_bbox().centroid()[axis];});
  left_list.push_back(*start);
  for (auto p = start + 1; p < end; p++) {
  	BBox bb = (*p)->get_bbox();
  	if (bb.centroid()[axis] <= split)
  		left_list.push_back(*p);
  	else
  		right_list.push_back(*p);
  }
  if (right_list.empty()) {
  	right_list.push_back(left_list.back());
  	left_list.pop_back();
  }
	node->l = construct_bvh(left_list.begin(), left_list.end(), max_leaf_size);
  node->r = construct_bvh(right_list.begin(), right_list.end(), max_leaf_size);
	return node;
}

bool BVHAccel::has_intersection(const Ray &ray, BVHNode *node) const {
  // TODO (Part 2.3):
  // Fill in the intersect function.
  // Take note that this function has a short-circuit that the
  // Intersection version cannot, since it returns as soon as it finds
  // a hit, it doesn't actually have to find the closest hit.
  if (not node->bb.intersect(ray, ray.min_t, ray.max_t)) return false;
	if (node->isLeaf()) {
		for (auto p = node->start; p != node->end; p++) {
      total_isects++;
      if ((*p)->has_intersection(ray))
        return true;
    }
		return false;
	}
	return has_intersection(ray, node->l) or has_intersection(ray, node->r);
}

bool BVHAccel::intersect(const Ray &ray, Intersection *i, BVHNode *node) const {
  // TODO (Part 2.3):
  // Fill in the intersect function.
	if (not node->bb.intersect(ray, ray.min_t, ray.max_t)) {
		return false;
	}
	if (node->isLeaf()) {
		bool hit = false;
		for (auto p = node->start; p != node->end; p++) {
      total_isects++;
      if ((*p)->intersect(ray, i))
      	hit = true;
    }
		return hit;
	}
	bool i_left = intersect(ray, i, node->l);
	bool i_right = intersect(ray, i, node->r);
	return i_left or i_right;
}

} // namespace SceneObjects
} // namespace CGL
