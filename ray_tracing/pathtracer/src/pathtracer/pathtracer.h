#ifndef CGL_PATHTRACER_H
#define CGL_PATHTRACER_H

#include "CGL/timer.h"

#include "scene/bvh.h"
#include "pathtracer/sampler.h"
#include "pathtracer/intersection.h"

#include "application/renderer.h"

#include "scene/scene.h"
using CGL::SceneObjects::Scene;

#include "scene/environment_light.h"
using CGL::SceneObjects::EnvironmentLight;

using CGL::SceneObjects::BVHNode;
using CGL::SceneObjects::BVHAccel;

namespace CGL {

    class PathTracer {
    public:
        PathTracer();
        ~PathTracer();

        /**
         * Sets the pathtracer's frame size. If in a running state (VISUALIZE,
         * RENDERING, or DONE), transitions to READY b/c a changing window size
         * would invalidate the output. If in INIT and configuration is done,
         * transitions to READY.
         * \param width width of the frame
         * \param height height of the frame
         */
        void set_frame_size(size_t width, size_t height);

        void write_to_framebuffer(ImageBuffer& framebuffer, size_t x0, size_t y0, size_t x1, size_t y1);

        /**
         * If the pathtracer is in READY, delete all internal data, transition to INIT.
         */
        void clear();

        /**
         * Trace an ray in the scene.
         */
        Spectrum estimate_direct_lighting_hemisphere(const Ray& r, const SceneObjects::Intersection& isect);
        Spectrum estimate_direct_lighting_importance(const Ray& r, const SceneObjects::Intersection& isect);

        Spectrum est_radiance_global_illumination(const Ray& r);
        Spectrum zero_bounce_radiance(const Ray& r, const SceneObjects::Intersection& isect);
        Spectrum one_bounce_radiance(const Ray& r, const SceneObjects::Intersection& isect);
        Spectrum at_least_one_bounce_radiance(const Ray& r, const SceneObjects::Intersection& isect);

        double estimate_direct_lighting_hemisphere_by_wavelength(const Ray& r, const SceneObjects::Intersection& isect);
        double estimate_direct_lighting_importance_by_wavelength(const Ray& r, const SceneObjects::Intersection& isect);
        double est_radiance_global_illumination_by_wavelength(const Ray& r);
        double zero_bounce_radiance_by_wavelength(const Ray& r, const SceneObjects::Intersection& isect);
        double one_bounce_radiance_by_wavelength(const Ray& r, const SceneObjects::Intersection& isect);
        double at_least_one_bounce_radiance_by_wavelength(const Ray& r, const SceneObjects::Intersection& isect);

        Spectrum debug_shading(const Vector3D& d) {
            return Vector3D(abs(d.r), abs(d.g), .0).unit();
        }

        Spectrum normal_shading(const Vector3D& n) {
            return n * .5 + Spectrum(.5);
        }

        static float gaussian(float x, float mu, float sigma) {
					return 1. / (sigma * sqrt(2 * PI)) * exp(-0.5 * pow((x - mu) / sigma, 2));
				}

				constexpr static float mu_red = 600;
        constexpr static float mu_green = 550;
        constexpr static float mu_blue = 450;
        constexpr static float sigma_red = 25;
        constexpr static float sigma_green = 25;
        constexpr static float sigma_blue = 15;

        /**
         * Trace a camera ray given by the pixel coordinate.
         */
        void raytrace_pixel(size_t x, size_t y);

        void raytrace_pixel_by_wavelength(size_t x, size_t y);

        static float sample_wavelength(float &pdf) {
        	pdf = 1. / 300.;
					return random_uniform() * 300 + 400;
				}

				static Spectrum get_response(float wavelength) {
//        	return Vector3D(0.1, 0, 0);
					float r, g, b;
					r = PathTracer::gaussian(wavelength, PathTracer::mu_red, PathTracer::sigma_red);
					g = PathTracer::gaussian(wavelength, PathTracer::mu_green, PathTracer::sigma_green);
					b = PathTracer::gaussian(wavelength, PathTracer::mu_blue, PathTracer::sigma_blue);
					return Spectrum(r, g, b);
				}

        // Integrator sampling settings //

        size_t max_ray_depth; ///< maximum allowed ray depth (applies to all rays)
        size_t ns_aa;         ///< number of camera rays in one pixel (along one axis)
        size_t ns_pp;         ///< number of camera rays in one point
        size_t ns_area_light; ///< number samples per area light source
        size_t ns_diff;       ///< number of samples - diffuse surfaces
        size_t ns_glsy;       ///< number of samples - glossy surfaces
        size_t ns_refr;       ///< number of samples - refractive surfaces

        size_t samplesPerBatch;
        float maxTolerance;
        bool direct_hemisphere_sample; ///< true if sampling uniformly from hemisphere for direct lighting. Otherwise, light sample

        // Components //

        BVHAccel* bvh;                 ///< BVH accelerator aggregate
        EnvironmentLight* envLight;    ///< environment map
        Sampler2D* gridSampler;        ///< samples unit grid
        Sampler3D* hemisphereSampler;  ///< samples unit hemisphere
        HDRImageBuffer sampleBuffer;   ///< sample buffer
        Timer timer;                   ///< performance test timer

        std::vector<int> sampleCountBuffer;   ///< sample count buffer

        Scene* scene;         ///< current scene
        Camera* camera;       ///< current camera

        // Tonemapping Controls //

        float tm_gamma;                           ///< gamma
        float tm_level;                           ///< exposure level
        float tm_key;                             ///< key value
        float tm_wht;                             ///< white point
    };

}  // namespace CGL

#endif  // CGL_RAYTRACER_H
