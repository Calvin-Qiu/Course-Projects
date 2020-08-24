#include "pathtracer.h"

#include "scene/light.h"
#include "scene/sphere.h"
#include "scene/triangle.h"


using namespace CGL::SceneObjects;

namespace CGL {

PathTracer::PathTracer() {
  gridSampler = new UniformGridSampler2D();
  hemisphereSampler = new UniformHemisphereSampler3D();

  tm_gamma = 2.2f;
  tm_level = 1.0f;
  tm_key = 0.18;
  tm_wht = 5.0f;
}

PathTracer::~PathTracer() {
  delete gridSampler;
  delete hemisphereSampler;
}

void PathTracer::set_frame_size(size_t width, size_t height) {
  sampleBuffer.resize(width, height);
  sampleCountBuffer.resize(width * height);
}

void PathTracer::clear() {
  bvh = NULL;
  scene = NULL;
  camera = NULL;
  sampleBuffer.clear();
  sampleCountBuffer.clear();
  sampleBuffer.resize(0, 0);
  sampleCountBuffer.resize(0, 0);
}

void PathTracer::write_to_framebuffer(ImageBuffer &framebuffer, size_t x0,
                                      size_t y0, size_t x1, size_t y1) {
  sampleBuffer.toColor(framebuffer, x0, y0, x1, y1);
}

Spectrum
PathTracer::estimate_direct_lighting_hemisphere(const Ray &r,
                                                const Intersection &isect) {
  // Estimate the lighting from this intersection coming directly from a light.
  // For this function, sample uniformly in a hemisphere.

  // make a coordinate system for a hit point
  // with N aligned with the Z direction.
  Matrix3x3 o2w;
  make_coord_space(o2w, isect.n);
  Matrix3x3 w2o = o2w.T();

  // w_out points towards the source of the ray (e.g.,
  // toward the camera if this is a primary ray)
  const Vector3D &hit_p = r.o + r.d * isect.t;
  const Vector3D &w_out = w2o * (-r.d);

  // This is the same number of total samples as
  // estimate_direct_lighting_importance (outside of delta lights). We keep the
  // same number of samples for clarity of comparison.
  int num_samples = scene->lights.size() * ns_area_light;
  Spectrum L_out;

  // TODO (Part 3): Write your sampling loop here
  // TODO BEFORE YOU BEGIN
  // UPDATE `est_radiance_global_illumination` to return direct lighting instead of normal shading
  for (int s = 0; s < num_samples; s++) {
  	Vector3D w_in = hemisphereSampler->get_sample();
  	Ray new_ray = Ray(hit_p, o2w * w_in);
  	new_ray.min_t = EPS_F;
  	Intersection new_isect;
  	if (bvh->intersect(new_ray, &new_isect)) {
			Spectrum emitted = zero_bounce_radiance(new_ray, new_isect);
			Spectrum f = isect.bsdf->f(w_out, w_in);
			Spectrum L_sample = f * emitted * dot(o2w * w_in, isect.n) * 2 * PI;
		  L_out += L_sample;
  	}
  }
  L_out /= num_samples;
  return L_out;
}

Spectrum PathTracer::estimate_direct_lighting_importance(const Ray &r,
                                                const Intersection &isect) {
  // Estimate the lighting from this intersection coming directly from a light.
  // To implement importance sampling, sample only from lights, not uniformly in
  // a hemisphere.

  // make a coordinate system for a hit point
  // with N aligned with the Z direction.
  Matrix3x3 o2w;
  make_coord_space(o2w, isect.n);
  Matrix3x3 w2o = o2w.T();

  // w_out points towards the source of the ray (e.g.,
  // toward the camera if this is a primary ray)
  const Vector3D &hit_p = r.o + r.d * isect.t;
  const Vector3D &w_out = w2o * (-r.d);
	//ns_area_light per light except delta
  Spectrum L_out;
  // TODO (Part 3): Write your sampling loop here
  // TODO BEFORE YOU BEGIN
  // UPDATE `est_radiance_global_illumination` to return direct lighting instead of normal shading
  for (auto light : scene->lights) {
  	Spectrum L_light;
  	size_t ns = light->is_delta_light() ? 1 : ns_area_light;
  	for (size_t s = 0; s < ns; s++) {
  		Vector3D w_in;
  		float distToLight;
  		float pdf;
  		Spectrum emitted = light->sample_L(hit_p, &w_in, &distToLight, &pdf);
  		Ray shadow = Ray(hit_p, w_in);
  		shadow.min_t = EPS_F;
			Intersection new_isect;
			if (bvh->intersect(shadow, &new_isect) and new_isect.t < distToLight - EPS_F) {
				continue;
			}
			Spectrum f = isect.bsdf->f(w_out, w2o * w_in);
			L_light += f * emitted * max(0., dot(w_in, isect.n)) / pdf;
  	}
  	L_out += L_light / ns;
  }
  L_out /= scene->lights.size();
  return L_out;
  }

Spectrum PathTracer::zero_bounce_radiance(const Ray &r,
                                          const Intersection &isect) {
  // TODO: Part 3, Task 2
  // Returns the light that results from no bounces of light
  return isect.bsdf->get_emission();
}

Spectrum PathTracer::one_bounce_radiance(const Ray &r,
                                         const Intersection &isect) {
  // TODO: Part 3, Task 3
  // Returns either the direct illumination by hemisphere or importance sampling
  // depending on `direct_hemisphere_sample`
	return estimate_direct_lighting_importance(r, isect);
}

Spectrum PathTracer::at_least_one_bounce_radiance(const Ray &r,
                                                  const Intersection &isect) {

	Spectrum L_out;
	if (r.depth == max_ray_depth) return L_out;
	L_out += one_bounce_radiance(r, isect);
  float cpdf = 0.65;
  Matrix3x3 o2w;
  make_coord_space(o2w, isect.n);
  Matrix3x3 w2o = o2w.T();
  Vector3D hit_p = r.o + r.d * isect.t;
  Vector3D w_out = w2o * (-r.d);
  Vector3D w_in;
	if (coin_flip(cpdf) or r.depth == 0) {
		float pdf;
		isect.bsdf->sample_f(w_out, &w_in, &pdf);
		Ray new_ray = Ray(hit_p, o2w * w_in);
		new_ray.min_t = EPS_F;
		new_ray.depth = r.depth + 1;
    Intersection new_isect;
    if (bvh->intersect(new_ray, &new_isect)){
    	Spectrum f = isect.bsdf->f(w_out, w_in);
			Spectrum L_sample = 1 / cpdf * 1 / pdf * f * at_least_one_bounce_radiance(new_ray, new_isect) * dot(o2w * w_in, isect.n);
			L_out += L_sample;
    }
	}
  return L_out;
}

Spectrum PathTracer::est_radiance_global_illumination(const Ray &r) {
  Intersection isect;
  Spectrum L_out;

  // You will extend this in assignment 3-2.
  // If no intersection occurs, we simply return black.
  // This changes if you implement hemispherical lighting for extra credit.

  if (!bvh->intersect(r, &isect))
    return L_out;

  // The following line of code returns a debug color depending
  // on whether ray intersection with triangles or spheres has
  // been implemented.

  // REMOVE THIS LINE when you are ready to begin Part 3.
//  L_out = (isect.t == INF_D) ? debug_shading(r.d) : normal_shading(isect.n);
	L_out = zero_bounce_radiance(r, isect);
  // TODO (Part 3): Return the direct illumination.
  L_out += at_least_one_bounce_radiance(r, isect);

  // TODO (Part 4): Accumulate the "direct" and "indirect"
  // parts of global illumination into L_out rather than just direct

  return L_out;
}

void PathTracer::raytrace_pixel(size_t x, size_t y) {

  // TODO (Part 1.1):
  // Make a loop that generates num_samples camera rays and traces them
  // through the scene. Return the average Spectrum.
  // You should call est_radiance_global_illumination in this function.

  // TODO (Part 5):
  // Modify your implementation to include adaptive sampling.
  // Use the command line parameters "samplesPerBatch" and "maxTolerance"
  int num_samples = ns_aa;          // total samples to evaluate
  Vector2D r0 = Vector2D(x, y); // bottom left corner of the pixel
  Spectrum sum;
  double s1 = 0;
  double s2 = 0;
  double mu;
  double sigma2;
  double I;
  int n = 0;
  for (int i = 0; i < num_samples; i++, n++) {
  	if (i >= samplesPerBatch and i % samplesPerBatch == 0) {
  		mu = s1 / i;
  		sigma2 = 1. / (i - 1) * (s2 - s1 * s1 / i);
  		I = 1.96 * sqrt(sigma2 / i);
  		if (I <= maxTolerance * mu)
  			break;
  	}
  	Vector2D dr = gridSampler->get_sample();
  	Vector2D r = r0 + dr;
  	Ray ray = camera->generate_ray_relativistic(r.x / sampleBuffer.w, r.y / sampleBuffer.h);
  	ray.depth = 0;
  	Spectrum sample = est_radiance_global_illumination(ray);
  	s1 += sample.illum();
  	s2 += sample.illum() * sample.illum();
  	sum += sample;
  }
	Spectrum avg = sum / n;
  sampleBuffer.update_pixel(avg, x, y);
  sampleCountBuffer[x + y * sampleBuffer.w] = n;
}


// Wavelength-dependent ray tracing

double PathTracer::estimate_direct_lighting_importance_by_wavelength(const Ray &r,
                                                const Intersection &isect) {
  // Estimate the lighting from this intersection coming directly from a light.
  // To implement importance sampling, sample only from lights, not uniformly in
  // a hemisphere.

  // make a coordinate system for a hit point
  // with N aligned with the Z direction.
  Matrix3x3 o2w;
  make_coord_space(o2w, isect.n);
  Matrix3x3 w2o = o2w.T();

  // w_out points towards the source of the ray (e.g.,
  // toward the camera if this is a primary ray)
  const Vector3D &hit_p = r.o + r.d * isect.t;
  const Vector3D &w_out = w2o * (-r.d);
	//ns_area_light per light except delta
  double L_out = 0;
  // UPDATE `est_radiance_global_illumination` to return direct lighting instead of normal shading
  for (auto light : scene->lights) {
  	double L_light = 0;
  	size_t ns = light->is_delta_light() ? 1 : ns_area_light;
  	for (size_t s = 0; s < ns; s++) {
  		Vector3D w_in;
  		float distToLight;
  		float pdf;
  		double emitted = light->sample_L(r.wavelength, hit_p, &w_in, &distToLight, &pdf);
  		Ray shadow = Ray(hit_p, w_in);
  		shadow.min_t = EPS_F;
			Intersection new_isect;
			if (bvh->intersect(shadow, &new_isect) and new_isect.t < distToLight - EPS_F) {
				continue;
			}
			double f = isect.bsdf->f(w_out, w2o * w_in, r.wavelength);
			double reflected = f * emitted * max(0., dot(w_in, isect.n)) / pdf;
			L_light += reflected;
			if (reflected != 0) {
			}
  	}
  	L_out += L_light / ns;
  }
  L_out /= scene->lights.size();
  return L_out;
  }

double PathTracer::zero_bounce_radiance_by_wavelength(const Ray &r,
                                          const Intersection &isect) {
  // TODO: Part 3, Task 2
  // Returns the light that results from no bounces of light
  return isect.bsdf->get_emission(r.wavelength);
}

double PathTracer::one_bounce_radiance_by_wavelength(const Ray &r,
                                         const Intersection &isect) {
  // TODO: Part 3, Task 3
  // Returns either the direct illumination by hemisphere or importance sampling
  // depending on `direct_hemisphere_sample`
	return estimate_direct_lighting_importance_by_wavelength(r, isect);
}

double PathTracer::at_least_one_bounce_radiance_by_wavelength(const Ray &r,
                                                  const Intersection &isect) {

	double L_out = 0;
	if (r.depth == max_ray_depth) return L_out;
	L_out += one_bounce_radiance_by_wavelength(r, isect);
  float cpdf = 0.65;
  Matrix3x3 o2w;
  make_coord_space(o2w, isect.n);
  Matrix3x3 w2o = o2w.T();
  Vector3D hit_p = r.o + r.d * isect.t;
  Vector3D w_out = w2o * (-r.d);
  Vector3D w_in;
	if (coin_flip(cpdf) or r.depth == 0) {
		float pdf;
		isect.bsdf->sample_f(w_out, &w_in, &pdf);
		Ray new_ray = Ray(hit_p, o2w * w_in);
		new_ray.min_t = EPS_F;
		new_ray.depth = r.depth + 1;
		new_ray.wavelength = r.wavelength;
    Intersection new_isect;
    if (bvh->intersect(new_ray, &new_isect)){
    	double f = isect.bsdf->f(w_out, w_in, new_ray.wavelength);
			double L_sample = 1 / cpdf * 1 / pdf * f * at_least_one_bounce_radiance_by_wavelength(new_ray, new_isect) * dot(o2w * w_in, isect.n);
			L_out += L_sample;
    }
	}
  return L_out;
}

double PathTracer::est_radiance_global_illumination_by_wavelength(const Ray &r) {
  Intersection isect;
  double L_out = 0;
  if (!bvh->intersect(r, &isect))
    return L_out;
	L_out = zero_bounce_radiance_by_wavelength(r, isect);
  L_out += at_least_one_bounce_radiance_by_wavelength(r, isect);
  return L_out;
}



void PathTracer::raytrace_pixel_by_wavelength(size_t x, size_t y) {

  int num_samples = ns_aa;
  int num_samples_per_point = ns_pp;
  Vector2D r0 = Vector2D(x, y); // bottom left corner of the pixel
  Spectrum sum;
  double s1 = 0;
  double s2 = 0;
  double mu;
  double sigma2;
  double I;
  int n = 0;
  for (int i = 0; i < num_samples; i++, n++) {
  	if (i >= samplesPerBatch and i % samplesPerBatch == 0) {
  		mu = s1 / i;
  		sigma2 = 1. / (i - 1) * (s2 - s1 * s1 / i);
  		I = 1.96 * sqrt(sigma2 / i);
  		if (I <= maxTolerance * mu)
  			break;
  	}
  	Vector2D dr = gridSampler->get_sample();
  	Vector2D r = r0 + dr;

  	Spectrum sample;
  	for (int j = 0; j < num_samples_per_point; j++) {
  		float pdf;
  		float wavelength = sample_wavelength(pdf);
  		Spectrum response = get_response(wavelength);
  	  Ray ray = camera->generate_ray_relativistic_by_wavelength(r.x / sampleBuffer.w, r.y / sampleBuffer.h, wavelength);
  	  ray.depth = 0;
  	  float intensity = est_radiance_global_illumination_by_wavelength(ray);
  	  sample += intensity * response / pdf;
  	}
  	sample /= num_samples_per_point;
  	s1 += sample.illum();
  	s2 += sample.illum() * sample.illum();
  	sum += sample;
  }
	Spectrum avg = sum / n;
  sampleBuffer.update_pixel(avg, x, y);
  sampleCountBuffer[x + y * sampleBuffer.w] = n;
}

} // namespace CGL