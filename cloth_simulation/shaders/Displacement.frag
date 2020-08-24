#version 330

uniform vec3 u_cam_pos;
uniform vec3 u_light_pos;
uniform vec3 u_light_intensity;

uniform vec4 u_color;

uniform sampler2D u_texture_2;
uniform vec2 u_texture_2_size;

uniform float u_normal_scaling;
uniform float u_height_scaling;

in vec4 v_position;
in vec4 v_normal;
in vec4 v_tangent;
in vec2 v_uv;

out vec4 out_color;

float h(vec2 uv) {
  // You may want to use this helper function...
  return texture(u_texture_2, uv).r;
}

void main() {
  // YOUR CODE HERE
  float width = u_texture_2_size.x;
  float height = u_texture_2_size.y;
  float du = u_normal_scaling * u_height_scaling * (h(v_uv + vec2(1 / width, 0)) - h(v_uv));
  float dv = u_normal_scaling * u_height_scaling * (h(v_uv + vec2(0, 1 / height)) - h(v_uv));
  vec3 n = vec3(-du, -dv, 1);
  n /= length(n);
  mat3 TBN = mat3(vec3(v_tangent), cross(vec3(normalize(v_normal)), vec3(v_tangent)), vec3(normalize(v_normal)));
  n = normalize(TBN * n);
  float k_diffuse = 1.0;
  vec3 l = (u_light_pos - vec3(v_position));
  float r = length(l);
  l /= r;
  float cosine = dot(n, l);
  vec4 out_diffuse = k_diffuse * vec4(u_light_intensity, 0) * max(0, cosine) / r / r ;

  vec4 out_ambient = vec4(0, 0, 0, 0);

  float k_specular = 1;
  float p = 5.0;
  vec3 view = u_cam_pos - vec3(v_position);
  view /= length(view);
  vec3 half_vector = normalize(0.5 * (view + l));
  vec4 out_specular = k_specular * vec4(u_light_intensity, 0) * pow(max(0, dot(n, half_vector)), p) / r / r ;

  out_color = out_ambient + out_specular + out_diffuse;
  out_color.a = 1;
}

