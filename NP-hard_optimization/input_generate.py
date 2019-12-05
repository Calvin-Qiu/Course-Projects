import random
import sys

if len(sys.argv) != 4:
    # Wrong number of arguments, tell the user what you expected
    # Note that sys.argv[0] is how the user called the python script
    print("USAGE: %s <number of vertices> <probability of home> <output filename>"%(sys.argv[0]))
    # End the program
    sys.exit(1)


def print_input(L, E, H, s, fileName):
	""" L is a list of locations ordered by their id, L[i] is the name of the i-th location
		E is an adjacency matrix whose entries are weights, where E[i][j] denotes an edge from i to j
		E[i][j] == 'x' if and only if such an edge does not exist
		H is a list of homes identified by id
		s is the starting location
		fileName is name of the file to write to
	"""
	f = open(fileName, 'w')
	f.write(str(len(L))+'\n') #The first line of the input should contain a single integer, which equals the number of locations
	f.write(str(len(H))+'\n') #The second line should also be an integer, which equals the number of homes
	for location in L:
		f.write(location+' ')
	f.write('\n')
	for home_id in H:
		f.write(L[home_id]+' ')
	f.write('\n')
	f.write(s+'\n')
	for i in range(len(E)):
		for j in range(len(E)):
			f.write(str(E[i][j]) + ' ')
		f.write('\n')
	f.close()

def generate_random_input(n, p, fileName):
	""" Generate a random input of n locations and write to fileName 
		Each vertex is a home with probability p
	"""

	max_x = 1000
	L = []
	H = []
	E = []
	x = [] #non negative x-coordinate of vertices
	for i in range(n):
		L.append('location' + str(i))
		rand = round(random.random() * max_x) + 1
		while rand in x:
			rand = round(random.random() * max_x) + 1
		x.append(rand)
	for i in range(n):
		if random.random() < p and len(H) < n / 2: #vertex is a home with probability p
			H.append(i)
	for i in range(n):
		E.append([])
		for j in range(0, i):
			E[i].append(abs(x[i] - x[j])) #E[i][j] = absolute value of difference in x-coordinates of vertex i and vertex j as weight to ensure triangular inequality
		E[i].append('x') #no self-edges
	for i in range(n):
		for j in range(i+1, n):
			E[i].append(E[j][i])
	starting_index = int((random.random() * (len(L) - 1)) // 1)
	s = L[starting_index]
	print_input(L, E, H, s, fileName)

generate_random_input(int(sys.argv[1]), float(sys.argv[2]), sys.argv[3])