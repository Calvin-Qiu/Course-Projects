#include <assert.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>

// Include SSE intrinsics
#if defined(_MSC_VER)
#include <intrin.h>
#elif defined(__GNUC__) && (defined(__x86_64__) || defined(__i386__))
#include <immintrin.h>
#include <x86intrin.h>
#endif

// Include OpenMP
#include <omp.h>

#include "layers.h"
#include "volume.h"

conv_layer_t *make_conv_layer(int input_width, int input_height, int input_depth, int filter_width, int num_filters,
        int stride, int pad) {
    conv_layer_t *l = (conv_layer_t *) malloc(sizeof(conv_layer_t));

    l->output_depth = num_filters;
    l->filter_width = filter_width;
    l->input_depth = input_depth;
    l->input_width = input_width;
    l->input_height = input_height; 

    l->filter_height = l->filter_width;
    l->stride = stride;
    l->pad = pad;

    l->output_width = (l->input_width + l->pad * 2 - l->filter_width) /
        l->stride + 1;
    l->output_height = (l->input_height + l->pad * 2 - l->filter_height) /
        l->stride + 1;

    l->filters = malloc(sizeof(volume_t *) * num_filters);
    for (int i = 0; i < num_filters; i++) {
        l->filters[i] = make_volume(l->filter_width, l->filter_height,
            l->input_depth, 0.0);
    }

    l->bias = 0.0;
    l->biases = make_volume(1, 1, l->output_depth, l->bias);

    return l;
} 

// Performs the forward pass for a convolutional layer by convolving each one
// of the filters with a particular input, and placing the result in the output
// array.
//
// One way to think about convolution in this case is that we have one of the
// layer's filters (a 3D array) that is superimposed on one of the layer's
// inputs (a second 3D array) that has been implicitly padded with zeros. Since
// convolution is a sum of products (described below), we don't actually have
// to add any zeros to the input volume since those terms will not contribute
// to the convolution. Instead, for each position in the filter, we just make
// sure that we are in bounds for the input volume.
//
// Essentially, the filter is "sliding" across the input, in both the x and y
// directions, where we increment our position in each direction by using the
// stride parameter.
//
// At each position, we compute the sum of the elementwise product of the filter
// and the part of the array it's covering. For instance, let's consider a 2D
// case, where the filter (on the left) is superimposed on some part of the
// input (on the right).
//
//   Filter             Input
//  -1  0  1           1  2  3
//  -1  0  1           4  5  6
//  -1  0  1           7  8  9
//
// Here, the sum of the elementwise product is:
//    Filter[0][0] * Input[0][0] + Filter[0][1] * Input[0][1] + ...
//    = -1 * 1 + 0 * 2 + ... + 0 * 8 + 1 * 9
//    = 6
//
// The 3D case is essentially the same, we just have to sum over the other
// dimension as well. Also, since volumes are internally represented as 1D
// arrays, we must use the volume_get and volume_set commands to access elements
// at a coordinate (x, y, d). Finally, we add the corresponding bias for the
// filter to the sum before putting it into the output volume.
// void conv_forward(conv_layer_t *l, volume_t **inputs, volume_t **outputs, int start, int end) {

void conv_forward16(conv_layer_t *l, volume_t **inputs, volume_t **outputs, int start, int end) {

    volume_t *in = inputs[0];
    volume_t *out = outputs[0];
    double *in_weights = in->weights;
    int in_width = in->width;
    int in_depth = in->depth;
    int in_height = in->height;
    int out_width = out->width;
    int out_depth = out->depth;
    double *out_weights = out->weights;

    int stride = l->stride;

    for(int f = 0; f < l->output_depth; f++) {
        volume_t *filter = l->filters[f];
        double *f_weights = filter->weights;
        int f_width = filter->width;
        int f_height = filter->height;
        int y = -l->pad;
        for(int out_y = 0; out_y < l->output_height; y += stride, out_y++) {
            int x = -l->pad;
            for(int out_x = 0; out_x < l->output_width; x += stride, out_x++) {

                // Take sum of element-wise product
                __m256d vec_sum = _mm256_set1_pd(0.0);
                    __m256d vec_filter1;
                    __m256d vec_filter2;
                    __m256d vec_filter3;
                    __m256d vec_filter4;
                    __m256d vec_in1;
                    __m256d vec_in2;
                    __m256d vec_in3;
                    __m256d vec_in4;
                    __m256d vec_prod;
                    double sum = 0.0;
                    for(int fy = 0; fy < f_height; fy++) {
                        int in_y = y + fy;
                        for(int fx = 0; fx < f_width; fx++) {
                            int in_x = x + fx;
                            if(in_y >= 0 && in_y < in_height && in_x >=0 && in_x < in_width) {
                                vec_filter1 = _mm256_loadu_pd(f_weights + ((f_width * fy) + fx) * 16);
                                vec_filter2 = _mm256_loadu_pd(f_weights + ((f_width * fy) + fx) * 16 + 4);
                                vec_filter3 = _mm256_loadu_pd(f_weights + ((f_width * fy) + fx) * 16 + 8);
                                vec_filter4 = _mm256_loadu_pd(f_weights + ((f_width * fy) + fx) * 16 + 12);

                                vec_in1 = _mm256_loadu_pd(in_weights + ((in_width * in_y) + in_x) * in_depth);
                                vec_in2 = _mm256_loadu_pd(in_weights + ((in_width * in_y) + in_x) * in_depth + 4);
                                vec_in3 = _mm256_loadu_pd(in_weights + ((in_width * in_y) + in_x) * in_depth + 8);
                                vec_in4 = _mm256_loadu_pd(in_weights + ((in_width * in_y) + in_x) * in_depth + 12);

                                vec_prod = _mm256_mul_pd(vec_filter1, vec_in1);
                                vec_sum = _mm256_add_pd(vec_sum, vec_prod);
                                vec_prod = _mm256_mul_pd(vec_filter2, vec_in2);
                                vec_sum = _mm256_add_pd(vec_sum, vec_prod);
                                vec_prod = _mm256_mul_pd(vec_filter3, vec_in3);
                                vec_sum = _mm256_add_pd(vec_sum, vec_prod);
                                vec_prod = _mm256_mul_pd(vec_filter4, vec_in4);
                                vec_sum = _mm256_add_pd(vec_sum, vec_prod);
                                
                            }
                        }
                    }
                    double *sum_arr = malloc(sizeof(double) * 4);
                    _mm256_storeu_pd(sum_arr, vec_sum);
                    sum += sum_arr[0] + sum_arr[1] + sum_arr[2] + sum_arr[3] + l->biases->weights[f];
                    out_weights[((out_width * out_y) + out_x) * out_depth + f] = sum;
                    free(sum_arr);
            }
        }
    }

}

void conv_forward20(conv_layer_t *l, volume_t **inputs, volume_t **outputs, int start, int end) {

    volume_t *in = inputs[0];
    volume_t *out = outputs[0];
    double *in_weights = in->weights;
    int in_width = in->width;
    int in_depth = in->depth;
    int in_height = in->height;
    int out_width = out->width;
    int out_depth = out->depth;
    double *out_weights = out->weights;

    int stride = l->stride;

    for(int f = 0; f < l->output_depth; f++) {
        volume_t *filter = l->filters[f];
        double *f_weights = filter->weights;
        int f_width = filter->width;
        int f_height = filter->height;
        int y = -l->pad;
        for(int out_y = 0; out_y < l->output_height; y += stride, out_y++) {
            int x = -l->pad;
            for(int out_x = 0; out_x < l->output_width; x += stride, out_x++) {

                // Take sum of element-wise product
                __m256d vec_sum = _mm256_set1_pd(0.0);
                    __m256d vec_filter1;
                    __m256d vec_filter2;
                    __m256d vec_filter3;
                    __m256d vec_filter4;
                    __m256d vec_filter5;
                    __m256d vec_in1;
                    __m256d vec_in2;
                    __m256d vec_in3;
                    __m256d vec_in4;
                    __m256d vec_in5;

                    __m256d vec_prod;
                    double sum = 0.0;
                    for(int fy = 0; fy < f_height; fy++) {
                        int in_y = y + fy;
                        for(int fx = 0; fx < f_width; fx++) {
                            int in_x = x + fx;
                            if(in_y >= 0 && in_y < in_height && in_x >=0 && in_x < in_width) {
                                vec_filter1 = _mm256_loadu_pd(f_weights + ((f_width * fy) + fx) * 20);
                                vec_filter2 = _mm256_loadu_pd(f_weights + ((f_width * fy) + fx) * 20 + 4);
                                vec_filter3 = _mm256_loadu_pd(f_weights + ((f_width * fy) + fx) * 20 + 8);
                                vec_filter4 = _mm256_loadu_pd(f_weights + ((f_width * fy) + fx) * 20 + 12);
                                vec_filter5 = _mm256_loadu_pd(f_weights + ((f_width * fy) + fx) * 20 + 16);

                                vec_in1 = _mm256_loadu_pd(in_weights + ((in_width * in_y) + in_x) * in_depth);
                                vec_in2 = _mm256_loadu_pd(in_weights + ((in_width * in_y) + in_x) * in_depth + 4);
                                vec_in3 = _mm256_loadu_pd(in_weights + ((in_width * in_y) + in_x) * in_depth + 8);
                                vec_in4 = _mm256_loadu_pd(in_weights + ((in_width * in_y) + in_x) * in_depth + 12);
                                vec_in5 = _mm256_loadu_pd(in_weights + ((in_width * in_y) + in_x) * in_depth + 16);

                                vec_prod = _mm256_mul_pd(vec_filter1, vec_in1);
                                vec_sum = _mm256_add_pd(vec_sum, vec_prod);

                                vec_prod = _mm256_mul_pd(vec_filter2, vec_in2);
                                vec_sum = _mm256_add_pd(vec_sum, vec_prod);                                
                                
                                vec_prod = _mm256_mul_pd(vec_filter3, vec_in3);
                                vec_sum = _mm256_add_pd(vec_sum, vec_prod);
                                
                                vec_prod = _mm256_mul_pd(vec_filter4, vec_in4);
                                vec_sum = _mm256_add_pd(vec_sum, vec_prod);
                               
                                vec_prod = _mm256_mul_pd(vec_filter5, vec_in5);
                                vec_sum = _mm256_add_pd(vec_sum, vec_prod);
                                
                            }
                        }
                    }
                    double *sum_arr = malloc(sizeof(double) * 4);
                    _mm256_storeu_pd(sum_arr, vec_sum);
                    sum += sum_arr[0] + sum_arr[1] + sum_arr[2] + sum_arr[3] + l->biases->weights[f];
                    out_weights[((out_width * out_y) + out_x) * out_depth + f] = sum;
                    free(sum_arr);
            }
        }
    }
}



void conv_forward3(conv_layer_t *l, volume_t **inputs, volume_t **outputs, int start, int end) {

    volume_t *in = inputs[0];
    volume_t *out = outputs[0];
    double *in_weights = in->weights;
    int in_width = in->width;
    int in_depth = in->depth;
    int in_height = in->height;
    int out_width = out->width;
    int out_depth = out->depth;
    double *out_weights = out->weights;

    int stride = l->stride;

    for(int f = 0; f < l->output_depth; f++) {
        volume_t *filter = l->filters[f];
        double *f_weights = filter->weights;
        int f_width = filter->width;
        int f_height = filter->height;
        int y = -l->pad;
        for(int out_y = 0; out_y < l->output_height; y += stride, out_y++) {
            int x = -l->pad;
            for(int out_x = 0; out_x < l->output_width; x += stride, out_x++) {

                // Take sum of element-wise product
                __m256d vec_sum = _mm256_set1_pd(0.0);
                __m256d vec_filter;
                __m256d vec_in;
                __m256d vec_prod;
                double sum = 0.0;
                for(int fy = 0; fy < f_height; fy++) {
                    int in_y = y + fy;
                    for(int fx = 0; fx < f_width; fx++) {
                        int in_x = x + fx;
                        if(in_y >= 0 && in_y < in_height && in_x >=0 && in_x < in_width) {
                            vec_filter = _mm256_loadu_pd(f_weights + ((f_width * fy) + fx) * 3);
                            vec_in = _mm256_loadu_pd(in_weights + ((in_width * in_y) + in_x) * in_depth);
                            vec_prod = _mm256_mul_pd(vec_filter, vec_in);
                            vec_sum = _mm256_add_pd(vec_sum, vec_prod);
                            
                        }
                    }
                }
                double *sum_arr = malloc(sizeof(double) * 4);
                _mm256_storeu_pd(sum_arr, vec_sum);
                sum += sum_arr[0] + sum_arr[1] + sum_arr[2] + l->biases->weights[f];
                out_weights[((out_width * out_y) + out_x) * out_depth + f] = sum;
                free(sum_arr);
            }
        }
    }

}


void conv_load(conv_layer_t *l, const char *file_name) {
    int filter_width, filter_height, depth, filters;

    FILE *fin = fopen(file_name, "r");

    fscanf(fin, "%d %d %d %d", &filter_width, &filter_height, &depth, &filters);
    assert(filter_width == l->filter_width);
    assert(filter_height == l->filter_height);
    assert(depth == l->input_depth); 
    assert(filters == l->output_depth);

    for(int f = 0; f < filters; f++) {
        for (int x = 0; x < filter_width; x++) {
            for (int y = 0; y < filter_height; y++) {
                for (int d = 0; d < depth; d++) {
                    double val;
                    fscanf(fin, "%lf", &val);
                    volume_set(l->filters[f], x, y, d, val);
                }
            }
        }
    }

    for(int d = 0; d < l->output_depth; d++) {
        double val;
        fscanf(fin, "%lf", &val);
        volume_set(l->biases, 0, 0, d, val);
    }

    fclose(fin);
}

relu_layer_t *make_relu_layer(int input_width, int input_height, int input_depth) {
    relu_layer_t *l = (relu_layer_t *) malloc(sizeof(relu_layer_t));

    l->input_depth = input_depth;
    l->input_width = input_width;
    l->input_height = input_height;

    l->output_width = l->input_width;
    l->output_height = l->input_height;
    l->output_depth = l->input_depth;

    return l;
}

// Applies the Rectifier Linear Unit (ReLU) function to the input, which sets
// output(x, y, d) to max(0.0, input(x, y, d)).
void relu_forward(relu_layer_t *l, volume_t **inputs, volume_t **outputs, int start, int end) {
    for (int i = start; i <= end; i++) {
        for (int x = 0; x < l->input_width; x++) {
            for (int y = 0; y < l->input_height; y++) {
                for (int d = 0; d < l->input_depth; d++) {
                    double value = (volume_get(inputs[i], x, y, d) < 0.0) ? 0.0 : volume_get(inputs[i], x, y, d);
                    volume_set(outputs[i], x, y, d, value);
                }
            }
        }
    } 
}

pool_layer_t *make_pool_layer(int input_width, int input_height, int input_depth, int pool_width, int stride) {
    pool_layer_t *l = (pool_layer_t *) malloc(sizeof(pool_layer_t));

    l->pool_width = pool_width;
    l->input_depth = input_depth;
    l->input_width = input_width;
    l->input_height = input_height;

    l->pool_height = l->pool_width;
    l->stride = stride;
    l->pad = 0;

    l->output_depth = input_depth;
    l->output_width = floor((l->input_width + l->pad * 2 - l->pool_width) / l->stride + 1);
    l->output_height = floor((l->input_height + l->pad * 2 - l->pool_height) / l->stride + 1);

    return l;
}

// This is like the convolutional layer in that we are sliding across the input
// volume, but instead of having a filter that we use to find the sum of an
// elementwise product, we instead just output the max value of some part of
// the image. For instance, if we consider a 2D case where the following is the
// part of the input that we are considering:
//
//     1 3 5
//     4 2 1
//     2 2 2
//
// then the value of the corresponding element in the output is 5 (since that
// is the maximum element). This effectively compresses the input.
void pool_forward(pool_layer_t *l, volume_t **inputs, volume_t **outputs, int start, int end) {
    for (int i = start; i <= end; i++) {
        volume_t *in = inputs[i];
        volume_t *out = outputs[i];

        int n = 0;
        for(int d = 0; d < l->output_depth; d++) {
            int x = -l->pad;
            for(int out_x = 0; out_x < l->output_width; x += l->stride, out_x++) {
                int y = -l->pad;
                for(int out_y = 0; out_y < l->output_height; y += l->stride, out_y++) {

                    double max = -INFINITY;
                    for(int fx = 0; fx < l->pool_width; fx++) {
                        for(int fy = 0; fy < l->pool_height; fy++) {
                            int in_y = y + fy;
                            int in_x = x + fx;
                            if(in_x >= 0 && in_x < in->width && in_y >= 0 && in_y < in->height) {
                                double v = volume_get(in, in_x, in_y, d);
                                if(v > max) {
                                    max = v;
                                }
                            }
                        }
                    }

                    n++;
                    volume_set(out, out_x, out_y, d, max);
                }
            }
        }
    }
}

fc_layer_t *make_fc_layer(int input_width, int input_height, int input_depth, int num_neurons) {
    fc_layer_t *l = (fc_layer_t *) malloc(sizeof(fc_layer_t));

    l->output_depth = num_neurons;
    l->input_depth = input_depth;
    l->input_width = input_width;
    l->input_height = input_height;

    l->num_inputs = l->input_width * l->input_height * l->input_depth;
    l->output_width = 1;
    l->output_height = 1;

    l->filters = (volume_t **) malloc(sizeof(volume_t *) * num_neurons);
    for (int i = 0; i < l->output_depth; i++) {
        l->filters[i] = make_volume(1, 1, l->num_inputs, 0.0);
    }

    l->bias = 0.0;
    l->biases = make_volume(1, 1, l->output_depth, l->bias);

    return l;
}

// Computes the dot product (i.e. the sum of the elementwise product) of the
// input's weights with each of the filters. Note that these filters are not
// the same as the filters for the convolutional layer.
void fc_forward(fc_layer_t *l, volume_t **inputs, volume_t **outputs, int start, int end) {
    for (int j = start; j <= end; j++) {
        volume_t *in = inputs[j];
        volume_t *out = outputs[j];
        double *in_weights = in->weights;
        double *out_weights = out->weights;

        for(int i = 0; i < l->output_depth;i++) {
            double dot = 0.0;
            for(int d = 0; d < l->num_inputs; d++) {
                dot += in_weights[d] * l->filters[i]->weights[d];
            }
            dot += l->biases->weights[i];
            out_weights[i] = dot;
        }
    }
}

void fc_load(fc_layer_t *l, const char *filename) {
    FILE *fin = fopen(filename, "r");

    int num_inputs;
    int output_depth;
    fscanf(fin, "%d %d", &num_inputs, &output_depth);
    assert(output_depth == l->output_depth);
    assert(num_inputs == l->num_inputs);

    for(int i = 0; i < l->output_depth; i++)
        for(int j = 0; j < l->num_inputs; j++) {
            fscanf(fin, "%lf", &(l->filters[i]->weights[j]));
        }

    for(int i = 0; i < l->output_depth; i++) {
        fscanf(fin, "%lf", &(l->biases->weights[i]));
    }

    fclose(fin);
}

softmax_layer_t *make_softmax_layer(int input_width, int input_height, int input_depth) {
    softmax_layer_t *l = (softmax_layer_t*) malloc(sizeof(softmax_layer_t));

    l->input_depth = input_depth;
    l->input_width = input_width;
    l->input_height = input_height;

    l->output_width = 1;
    l->output_height = 1;
    l->output_depth = l->input_width * l->input_height * l->input_depth;

    l->likelihoods = (double*) malloc(sizeof(double) * l->output_depth);

    return l;
}

// This function converts an input's weights array into a probability
// distribution by using the following formula:
//
// likelihood[i] = exp(in->weights[i]) / sum(exp(in->weights))
//
// To increase the numerical stability of taking the exponential of a value, we
// subtract the maximum input weights from each weight before taking the
// exponential. This yields exactly the same results as the expression above,
// but is more resilient to floating point errors.
void softmax_forward(softmax_layer_t *l, volume_t **inputs, volume_t **outputs, int start, int end) {
    double likelihoods[l->output_depth];

    volume_t *in = inputs[0];
    volume_t *out = outputs[0];
    double *in_weights = in->weights;
    double *out_weights = out->weights;

    // Compute max activation (used to compute exponentials)
    double amax = in_weights[0];
    for(int i = 1; i < l->output_depth; i++) {
        if (in_weights[i] > amax) {
            amax = in_weights[i];
        }
    }

    // Compute exponentials in a numerically stable way
    double total = 0.0;
    for(int i = 0; i < l->output_depth; i++) {
        double e = exp(in_weights[i] - amax);
        total += e;
        likelihoods[i] = e;
    }

    // Normalize and output to sum to one
    for(int i = 0; i < l->output_depth; i++) {
        out_weights[i] = likelihoods[i] / total;
    }

    
}
