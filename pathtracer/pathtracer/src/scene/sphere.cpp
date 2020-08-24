#include "sphere.h"

#include <cmath>

#include "pathtracer/bsdf.h"
#include "util/sphere_drawing.h"

namespace CGL {
namespace SceneObjects {

bool Sphere::test(const Ray &r, double &t1, double &t2) const {

  // TODO (Part 1.4):
  // Implement ray - sphere intersection test.
  // Return true if there are intersections and writing the
  // smaller of the two intersection times in t1 and the larger in t2.
	double a, b, c, t, delta2;
	a = r.d.norm2();
	b = 2 * dot(r.o - o, r.d);
	c = (r.o - o).norm2() - r2;
	delta2 = b * b - 4 * a * c;
	if (delta2 > 0) {
		t1 = (-b - sqrt(delta2)) / (2 * a);
		t2 = (-b + sqrt(delta2)) / (2 * a);
		return true;
	}
	return false;
}

bool Sphere::has_intersection(const Ray &r) const {

  // TODO (Part 1.4):
  // Implement ray - sphere intersection.
  // Note that you might want to use the the Sphere::test helper here.
	double t1, t2, t;
	if (test(r, t1, t2)) {
		if (r.min_t <= t2 and t1 <= r.max_t) {
			if (t1 >= r.min_t) {
				t = t1;
			} else if (t2 <= r.min_t) {
				t = t2;
			} else {
				return false;
			}
			r.max_t = t;
			return true;
		}
	}
	return false;
}

bool Sphere::intersect(const Ray &r, Intersection *i) const {

  // TODO (Part 1.4):
  // Implement ray - sphere intersection.
  // Note again that you might want to use the the Sphere::test helper here.
  // When an intersection takes place, the Intersection data should be updated
  // correspondingly.
	double t1, t2, t;
	if (test(r, t1, t2)) {
		if (r.min_t <= t2 and t1 <= r.max_t) {
			if (t1 >= r.min_t) {
				t = t1;
			} else if (t2 <= r.min_t) {
				t = t2;
			} else {
				return false;
			}
			Vector3D n = r.o + r.d * t - o;
			n.normalize();
			r.max_t = t;
			i->t = t;
			i->n = n;
			i->primitive = this;
			i->bsdf = get_bsdf();
			return true;
		}
	}
	return false;
}

void Sphere::draw(const Color &c, float alpha) const {
  Misc::draw_sphere_opengl(o, r, c);
}

void Sphere::drawOutline(const Color &c, float alpha) const {
  // Misc::draw_sphere_opengl(o, r, c);
}

} // namespace SceneObjects
} // namespace CGL
