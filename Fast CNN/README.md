This projects implements a few optimization strategies on a trained Convolutional Neural Networks for image classification. Following is a summary of the optimization:  
· The CNN runtime is analyzed using Gprof profiling  
· Achieved a 400% speedup by parallelizing the convolution computation with SIMD vector operations  
· Achieved another 400% speedup by implementing multi-threading using OpenMP  
· Achieved in total a 1600% speedup that significantly reduced the average runtime of the CNN  
A complete description of the project can be found here:  
https://inst.eecs.berkeley.edu/~cs61c/sp19/projects/proj4/  
