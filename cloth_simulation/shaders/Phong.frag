#version 330

uniform vec4 u_color;
uniform vec3 u_cam_pos;
uniform vec3 u_light_pos;
uniform vec3 u_light_intensity;

in vec4 v_position;
in vec4 v_normal;
in vec2 v_uv;

out vec4 out_color;

void main() {
  // YOUR CODE HERE
  float k_diffuse = 1.0;
  vec3 l = (u_light_pos - vec3(v_position));
  float r = length(l);
  l /= r;
  vec4 out_diffuse = k_diffuse * vec4(u_light_intensity, 0) * max(0, dot(vec3(normalize(v_normal)), l)) / r / r ;

  vec4 out_ambient = vec4(0.3, 0.4, 0.5, 0);

  float k_specular = 1.0;
  float p = 5.0;
  vec3 view = u_cam_pos - vec3(v_position);
  view /= length(view);
  vec3 half_vector = normalize(0.5 * (view + l));
  vec4 out_specular = k_specular * vec4(u_light_intensity, 0) * pow(max(0, dot(vec3(normalize(v_normal)), half_vector)), p) / r / r ;

  out_color = out_ambient + out_specular + out_diffuse;
  out_color.a = 1;
}

