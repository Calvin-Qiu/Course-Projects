import os
from solver import *
from output_validator import *
import time

input_path = './inputs7/'
output_path = './outputs/'
info = open('info.csv', 'w')
for filename in os.listdir(input_path):
	input_file_name = input_path + filename
	output_file_name = output_path + filename[:-2] + 'out'
	start = time.time()
	solve_from_file(input_file_name, output_path, ['cluster', '20', '5'])
	end = time.time()
	runtime = start - end
	_, cost, _ = validate_output(input_file_name, output_file_name)
	info.write('{}, {}, {}\n'.format(filename, cost, runtime))
info.close()


