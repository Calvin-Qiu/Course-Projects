import os
import sys
sys.path.append('..')
sys.path.append('../..')
import argparse
import utils
import copy

from student_utils import *
import networkx as nx
import datetime
from mip.model import *
import mip

"""
======================================================================
  Complete the following function.
======================================================================
"""


def solve(list_of_locations, list_of_homes, starting_car_location, adjacency_matrix, params=[]):
    """
    Write your algorithm here.
    Input:
        list_of_locations: A list of locations such that node i of the graph corresponds to name at index i of the list
        list_of_homes: A list of homes
        starting_car_location: The name of the starting location for the car
        adjacency_matrix: The adjacency matrix from the input file
    Output:
        A list of locations representing the car path
        A list of (location, [homes]) representing drop-offs
    """
    # name = params[0][:-3]
    # x0, D0 = get_solution(name, list_of_locations, adjacency_matrix)
    # print('Retrieved A-star solution')
    return solveWithILP(list_of_locations, list_of_homes, starting_car_location, adjacency_matrix, None, None)
        # if params[0] == 'greedy':
        #     return solveWithGreedy(list_of_locations, list_of_homes, starting_car_location, adjacency_matrix)


def get_solution(name, list_of_locations, adjacency_matrix):
    V = range(len(list_of_locations))
    output_name = "outputs/{}.out".format(name)
    with open(output_name, 'r') as f:
        content = f.readlines()
        # you may also want to remove whitespace characters like `\n` at the end of each line
    path_by_name = content[0].split()
    path = [list_of_locations.index(location) for location in path_by_name]
    x = [[0 for j in V] for i in V]
    last = path[0]
    for v in path[1:]:
        x[last][v] = 1
        last = v
    D = [[0 for j in V] for i in V]
    dropoffs  = content[2:]
    for dropoff in dropoffs:
        dropoff = dropoff.split()
        i = list_of_locations.index(dropoff[0])
        homes = [list_of_locations.index(h) for h in dropoff[1:]]
        for h in homes:
            D[i][h] = 1
    # x = [[0, 0, 0, 0, 0], 
    #      [0, 0, 0, 0, 0],
    #      [0, 0, 0, 1, 0],
    #      [0, 0, 1, 0, 0],
    #      [0, 0, 0, 0, 0]]
    # D = [[0, 0, 0, 0, 0],
    #      [0, 0, 0, 0, 0],
    #      [0, 0, 1, 0, 0],
    #      [0, 1, 0, 0, 0],
    #      [0, 0, 0, 0, 0]]
    # f = [[0, 0, 0, 0, 0, 0, 0],
    #      [0, 0, 0, 0, 0, 0, 0],
    #      [0, 0, 0, 1, 0, 0, 1],
    #      [0, 0, 0, 0, 0, 0, 1],
    #      [0, 0, 0, 0, 0, 0, 0],
    #      [0, 0, 2, 0, 0, 0, 0],
    #      [0, 0, 0, 0, 0, 0, 0]]
    # v = [0, 0, 1, 1, 0]
    return x, D

def solveWithILP(list_of_locations, list_of_homes, starting_car_location, adjacency_matrix, x0, D0):
    G, _ = adjacency_matrix_to_graph(adjacency_matrix)
    shortest_distances = dict(nx.all_pairs_dijkstra_path_length(G))
    num_of_locations = len(list_of_locations)
    V = list(range(num_of_locations))
    pairs = []
    for i in V:
        pairs.extend([(i,j) for j in V])
    H = [list_of_locations.index(h) for h in list_of_homes]
    VxH = []
    for i in V:
        for h in H:
            VxH.append((i, h))
    start = list_of_locations.index(starting_car_location)
    E = [(i, j) for (i, j) in pairs if adjacency_matrix[i][j] != 'x']
    in_list = [[j for j in V if adjacency_matrix[j][i] != 'x'] for i in V]
    out_list = in_list = [[j for j in V if adjacency_matrix[i][j] != 'x'] for i in V]
    dummy_source = num_of_locations
    dummy_sink = num_of_locations + 1
    m = Model()
    M = [[0 for j in V] for i in V]
    x = copy.deepcopy(M)
    D = copy.deepcopy(M)
    v = [m.add_var(name='v[{}]'.format(i), var_type=BINARY) for i in V]
    f = [[0 for j in V + [dummy_source, dummy_sink]] for i in V + [dummy_source, dummy_sink]]

    for i in V:
        for j in V:
            if adjacency_matrix[i][j] != 'x':
                x[i][j] = m.add_var(name='x[{}][{}]'.format(i, j), var_type=BINARY)
                m += v[i] >= x[i][j] # v[i] must be 1 if i has incident edges chosen
                f[i][j] = m.add_var(name='f[{}][{}]'.format(i, j), var_type=INTEGER, lb=0, ub=num_of_locations)
                m += f[i][j] <= num_of_locations * x[i][j] # can only send flow among chosen edges
            if j in H:
                D[i][j] = m.add_var(name='D[{}][{}]'.format(i, j), var_type=BINARY)
        f[i][dummy_sink] = m.add_var(name='f[{}][{}]'.format(i, dummy_sink), var_type=BINARY)
        #m += f[i][dummy_sink] <= v[i]
    f[dummy_source][start] = m.add_var(name='f[{}][{}]'.format(dummy_source, start), var_type=INTEGER, lb=0)

    for i in V:
        m += xsum(x[i][j] for j in out_list[i]) == xsum(x[j][i] for j in in_list[i]) # in-degree == out-degree
        if i in H:
            m += xsum(D[j][i] for j in V) == 1 # each home is dropped off exactly once
        for h in H:
            m += xsum(x[j][i] for j in in_list[i]) >= D[i][h] # if a home is dropped off at this vertex then its in-degree must be >= 1
        m += xsum(f[i][j] for j in out_list[i] + [dummy_sink]) == xsum(f[j][i] for j in in_list[i] + [dummy_source])
    m += f[dummy_source][start] == xsum(v[i] for i in V)

    m.objective = minimize( 2/3 * xsum(adjacency_matrix[i][j] * x[i][j] for (i, j) in E) + xsum(shortest_distances[i][h] * D[i][h] for (i, h) in pairs))

    max_seconds = 10
    if num_of_locations == 50:
        max_seconds = 2000
    elif num_of_locations == 100:
        max_seconds = 3600
    else:
        max_seconds = 5400

    status = m.optimize(max_seconds=max_seconds)
    if status == OptimizationStatus.OPTIMAL:
        print('optimal solution cost {} found'.format(m.objective_value))
    elif status == OptimizationStatus.FEASIBLE:
        print('sol.cost {} found, best possible: {}'.format(m.objective_value, m.objective_bound))
    elif status == OptimizationStatus.NO_SOLUTION_FOUND:
        print('no feasible solution found, lower bound is: {}'.format(m.objective_bound))
    # if status == OptimizationStatus.OPTIMAL or status == OptimizationStatus.FEASIBLE:
    #     print('solution:')
    #     for v in m.vars:
    #        if abs(v.x) > 1e-6: # only printing non-zeros
    #           print('{} : {}'.format(v.name, v.x))
    X = [[0 for j in V] for i in V]
    for (i, j) in E:
        X[i][j] = x[i][j].x
    tour = find_tour(X, start)
    dropoff_mapping = {}
    for i in V:
        drop = [h for h in H if D[i][h].x == 1]
        if drop:
            dropoff_mapping[i] = drop
    return tour, dropoff_mapping

def find_tour(adjacency_matrix, start):
    G = {}
    for i in range(len(adjacency_matrix)):
        #print('{}: {}'.format(i, [j for j in range(len(adjacency_matrix)) if adjacency_matrix[i][j] == 1]))
        edge_list = [j for j in range(len(adjacency_matrix)) if adjacency_matrix[i][j] == 1]
        if edge_list:
            G[i] = edge_list
    G = nx.DiGraph(G)
    tour_edges = list(nx.euler.eulerian_circuit(G, start))
    tour = [start]
    for e in tour_edges:
        tour.append(e[1])
    return tour


# def find_path(lp_matrix, start):
#     total = sum([sum(x) for x in lp_matrix])
#     #copy_matrix = copy.deepcopy(lp_matrix)
#     path = []
#     A = [path]
#     path.append(start)
#     print(start)
#     while(total != 0):
#         for j in range(len(lp_matrix)):
#             if sum(lp_matrix[start]) == 0:
#                 print('more than 1 cycle')
#                 for i in range(len(lp_matrix)):
#                     if sum(lp_matrix[i]) > 0:
#                         A.append(find_path(lp_matrix, i))
#                         return A
#             if (lp_matrix[start][j] == 1):
#                 lp_matrix[start][j] = 0
#                 start = j
#                 print(j)
#                 path.append(j)
#                 total -= 1
#                 break
#     return A



"""
======================================================================
   No need to change any code below this line
======================================================================
"""

"""
Convert solution with path and dropoff_mapping in terms of indices
and write solution output in terms of names to path_to_file + file_number + '.out'
"""
def convertToFile(path, dropoff_mapping, path_to_file, list_locs):
    string = ''
    for node in path:
        string += list_locs[node] + ' '
    string = string.strip()
    string += '\n'

    dropoffNumber = len(dropoff_mapping.keys())
    string += str(dropoffNumber) + '\n'
    for dropoff in dropoff_mapping.keys():
        strDrop = list_locs[dropoff] + ' '
        for node in dropoff_mapping[dropoff]:
            strDrop += list_locs[node] + ' '
        strDrop = strDrop.strip()
        strDrop += '\n'
        string += strDrop
    utils.write_to_file(path_to_file, string)

def solve_from_file(input_file, output_directory, params=[]):
    print('Processing', input_file)

    input_data = utils.read_file(input_file)
    num_of_locations, num_houses, list_locations, list_houses, starting_car_location, adjacency_matrix = data_parser(input_data)
    car_path, drop_offs = solve(list_locations, list_houses, starting_car_location, adjacency_matrix, params=params)

    basename, filename = os.path.split(input_file)
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    output_file = utils.input_to_output(input_file, output_directory)

    convertToFile(car_path, drop_offs, output_file, list_locations)


def solve_all(input_directory, output_directory, params=[]):
    input_files = utils.get_files_with_extension(input_directory, 'in')

    for input_file in input_files:
        solve_from_file(input_file, output_directory, params=params)


if __name__=="__main__":
    parser = argparse.ArgumentParser(description='Parsing arguments')
    parser.add_argument('--all', action='store_true', help='If specified, the solver is run on all files in the input directory. Else, it is run on just the given input file')
    parser.add_argument('input', type=str, help='The path to the input file or directory')
    parser.add_argument('output_directory', type=str, nargs='?', default='.', help='The path to the directory where the output should be written')
    parser.add_argument('params', nargs=argparse.REMAINDER, help='Extra arguments passed in')
    args = parser.parse_args()
    output_directory = args.output_directory
    if args.all:
        input_directory = args.input
        solve_all(input_directory, output_directory, params=args.params)
    else:
        input_file = args.input
        solve_from_file(input_file, output_directory, params=args.params)


