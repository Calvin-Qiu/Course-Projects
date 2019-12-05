from solver import *
from output_validator import *
import time

def aStarTest(n):
	input_file = './inputs/6.in'
	output_directory = './random_outputs/'
	output_file = './random_outputs/6.out'
	_, aStarCost, _ = validate_output(input_file, './outputs/6.out')
	count = 0
	total = 0
	for i in range(n):
		solve_from_file(input_file, output_directory, ['random'])
		_, cost, _ = validate_output(input_file, output_file)
		if cost > aStarCost:
			count += 1
		total += cost
	avg = total / n
	probability = count / n
	print('random solver achieves an average of {} \n a star achieves {}\n a star is better with probability {}'.format(avg, aStarCost, probability) )

def clusterTest(n, maxfileIndex):
	random_output_directory = './random_outputs/'
	cluster_output_directory = './cluster_outputs/'
	avgs = []
	probabilities = []
	clusterCosts = []
	runtime = []
	for fileIndex in range(maxfileIndex + 1):
		input_file = './inputs/' + str(fileIndex) + '.in'
		output_file = './random_outputs/' + str(fileIndex) + '.out'
		start = time.time()
		solve_from_file(input_file, cluster_output_directory, ['cluster', '20', '10'])
		end = time.time()
		runtime.append(end - start)
		_, clusterCost, _ = validate_output(input_file, './cluster_outputs/' + str(fileIndex) + '.out')
		count = 0
		total = 0
		invalid = 0
		for i in range(n):
			solve_from_file(input_file, random_output_directory, ['random'])
			_, cost, _ = validate_output(input_file, output_file)
			if cost != 'infinite':
				if cost > clusterCost:
					count += 1
				total += cost
			else:
				invalid += 1
		avgs.append(total / (n - invalid))
		probabilities.append(count / (n - invalid))
		clusterCosts.append(clusterCost)
	for fileIndex in range(maxfileIndex + 1):
		print('On input #{}:\n Random solver achieves an average of {} \n Cluster solver achieves {}\n Cluster solver took {} minites to run\n Cluster solver is better with probability {}'.format(fileIndex, avgs[fileIndex], clusterCosts[fileIndex], runtime[fileIndex] / 60 ,probabilities[fileIndex]))

def clusterTest(n, maxfileIndex):
	random_output_directory = './random_outputs/'
	cluster_output_directory = './cluster_outputs/'
	avgs = []
	probabilities = []
	clusterCosts = []
	runtime = []
	for fileIndex in range(maxfileIndex + 1):
		input_file = './inputs/' + str(fileIndex) + '.in'
		output_file = './random_outputs/' + str(fileIndex) + '.out'
		start = time.time()
		solve_from_file(input_file, cluster_output_directory, ['cluster', '20', '10'])
		end = time.time()
		runtime.append(end - start)
		_, clusterCost, _ = validate_output(input_file, './cluster_outputs/' + str(fileIndex) + '.out')
		count = 0
		total = 0
		invalid = 0
		for i in range(n):
			solve_from_file(input_file, random_output_directory, ['random'])
			_, cost, _ = validate_output(input_file, output_file)
			if cost != 'infinite':
				if cost > clusterCost:
					count += 1
				total += cost
			else:
				invalid += 1
		avgs.append(total / (n - invalid))
		probabilities.append(count / (n - invalid))
		clusterCosts.append(clusterCost)
	for fileIndex in range(maxfileIndex + 1):
		print('On input #{}:\n Random solver achieves an average of {} \n Cluster solver achieves {}\n Cluster solver took {} minites to run\n Cluster solver is better with probability {}'.format(fileIndex, avgs[fileIndex], clusterCosts[fileIndex], runtime[fileIndex] / 60 ,probabilities[fileIndex]))
