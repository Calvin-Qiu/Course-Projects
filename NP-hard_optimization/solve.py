import os
from ILP_2 import *
from output_validator import *
import time
import sys

input_file_path = sys.argv[1]
size = sys.argv[2]
info_file_name = sys.argv[3]
s = input_file_path.split('/')

ID = s[2]
input_name = s[3].split('.')[0]
input_size = input_name.split('_')[1]
print('-----You are using the right solver-----')
if size == input_size:
	output_path = './outputs2/{}/'.format(ID)
	output_file_path = output_path + input_name + '.out'
	old_output_file_path = './outputs/' + input_name + '.out'
	print(output_file_path)
	start = time.time()
	with open(info_file_name, 'a') as info:
		solve_from_file(input_file_path, output_path)
		end = time.time()
		runtime = end - start
		_, cost, _ = validate_output(input_file_path, output_file_path)
		_, old_cost, _ = validate_output(input_file_path, old_output_file_path)
		ratio = cost / (old_cost + 1)
		removed = 'kept'
		if ratio > 1:
			os.remove(output_file_path)
			removed = 'removed'
		print('new cost is {} times the old cost'.format(ratio))
		info.write('{}, {}, {}, {}, {}\n'.format(input_file_path, ratio, cost, runtime, removed))

	# except StopIteration:
	#   print("Time out")
	#   info.write('{}, {}, {}\n'.format(input_file_name, 'timeout', 'timeout'))
