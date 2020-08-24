#include "camera.h"

#include <iostream>
#include <sstream>
#include <fstream>

#include "CGL/misc.h"
#include "CGL/vector2D.h"
#include "CGL/vector3D.h"

using std::cout;
using std::endl;
using std::max;
using std::min;
using std::ifstream;
using std::ofstream;

namespace CGL {

using Collada::CameraInfo;

Ray Camera::generate_ray_for_thin_lens(double x, double y, double rndR, double rndTheta) const {
  // Part 2, Task 4:
  // compute position and direction of ray from the input sensor sample coordinate.
  // Note: use rndR and rndTheta to uniformly sample a unit disk.
  double deltaX = 2 * tan((0.5 * radians(hFov)));
  double deltaY = 2 * tan((0.5 * radians(vFov)));
	Vector3D pFilm = {-(x - 0.5) * deltaX, -(y - 0.5) * deltaY, 1};
	Vector3D pLens = {lensRadius * sqrt(rndR) * cos(rndTheta), lensRadius * sqrt(rndR) * sin(rndTheta), 0};
	Vector3D pFocus = - pFilm * focalDistance;
	Vector3D direction = pFocus - pLens;
	direction.normalize();
	Ray ray = Ray(pos + c2w * pLens, c2w * direction);
	double min_t = - nClip / direction.z;
  double max_t = - fClip / direction.z;
  ray.min_t = min_t;
  ray.max_t = max_t;
  return ray;
}


} // namespace CGL
