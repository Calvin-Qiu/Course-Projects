import os
import sys
sys.path.append('..')
sys.path.append('../..')
import argparse
import utils
from timeout import timeout
from student_utils import *
from itertools import chain, combinations
import networkx as nx
import random
import scipy
import datetime
from tsp_solver.greedy import solve_tsp

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
    if params:
        if params[0] == 'cluster':
            numClusters = int(params[1])
            numNearbyHomes = int(params[2])
            return solveWithClusters(list_of_locations, list_of_homes, starting_car_location, adjacency_matrix, numClusters, numNearbyHomes)
        if params[0] == 'astar':
            numNearbyHomes = int(params[1])
            return solveWithAStar(list_of_locations, list_of_homes, starting_car_location, adjacency_matrix, numNearbyHomes)
        if params[0] == 'random':
            return solveWithRandom(list_of_locations, list_of_homes, starting_car_location, adjacency_matrix)
        # if params[0] == 'greedy':
        #     return solveWithGreedy(list_of_locations, list_of_homes, starting_car_location, adjacency_matrix)

def solveWithClusters(list_of_locations, list_of_homes, starting_car_location, adjacency_matrix, numClusters, numNearbyHomes):
    print('Started at {}'.format(datetime.datetime.now()))
    shortest = getShortestDistances(adjacency_matrix)
    home_indices = [list_of_locations.index(home) for home in list_of_homes]
    start_index = list_of_locations.index(starting_car_location)
    centers, components, homesByComponents = findPartition(home_indices, adjacency_matrix, numClusters, shortest)
    clusters = [(centers[i], components[i], homesByComponents[i]) for i in range(len(centers))]
    componentPaths = []
    dropoffMapping = {}
    tourIndexMap = {}
    tourLocations = centers + [start_index] if start_index not in centers else centers
    for i in range(len(tourLocations)):
        tourIndexMap[i] = tourLocations[i] # i -> index of the i-th center in the original graph
    tourAdjacencyMatrix = makeLocalAdjacencyMatrix(tourLocations, adjacency_matrix) # adjacency matrix of only the clusters in new indicies, this reduces state space when doing A*
    # Tour = minTour(range(len(tourAdjacencyMatrix)), tourAdjacencyMatrix, tourLocations.index(start_index))
    startIndex = tourLocations.index(start_index)
    bestTourCost = float('inf')
    for endIndex in range(len(tourAdjacencyMatrix)):
        if endIndex != startIndex:
            tour = solve_tsp(tourAdjacencyMatrix, endpoints = (startIndex, endIndex))
            tour.append(startIndex)
            cost = 0
            lastIndex = startIndex
            for nextIndex in tour[1:]:
                cost += tourAdjacencyMatrix[lastIndex][nextIndex]
                lastIndex = nextIndex
            if cost < bestTourCost:
                bestTourCost = cost
                bestTour = tour
    globalTour, _ = GetGlobalRepresentation(tourIndexMap, tour, {})
    print('outer tour found at {}'.format(datetime.datetime.now()))
    numIter = 0
    for center, locations, homes in clusters:
        localAdjacencyMatrix = makeLocalAdjacencyMatrix(locations, adjacency_matrix)
        localIndexMap = {}
        for i in range(len(locations)):
            localIndexMap[i] = locations[i] # i -> index of the i-th location in the cluster in the original graph
        localHomeIndicies = [locations.index(h) for h in homes] # home indicies in local coordinates
        localStartIndex = locations.index(center)
        problem = DriveTAsHomeProblem(localAdjacencyMatrix, localHomeIndicies, localStartIndex, numNearbyHomes)
        localCarPath, localDropoffMapping = aStarSearch(problem, maxDistanceHeuristic)
        globalCarPath, globalDropoffMapping = GetGlobalRepresentation(localIndexMap, localCarPath, localDropoffMapping)
        componentPaths.append(globalCarPath)
        dropoffMapping.update(globalDropoffMapping)
        print('{}-th subtour found at {}'.format(numIter, datetime.datetime.now()))
        numIter += 1
    
    completePath = []
    for outIndex in globalTour:
        if outIndex in centers:
            completePath.extend(componentPaths[centers.index(outIndex)])
        else:
            completePath.append(outIndex)
    return completePath, dropoffMapping

def findPartition(home_indices, adjacency_matrix, numClusters, shortest): #numClusters = 10 works well
    """Returns the best partition (centers, components, homesByComponents) """
    numClusters = min(numClusters, len(adjacency_matrix) // 10 + 1)
    avergaeClusterSize = len(adjacency_matrix) // numClusters
    if not avergaeClusterSize:
        print('Error: cluster size 0')
        exit(1)
    attempts = min(int(scipy.special.binom(len(adjacency_matrix) - 1, avergaeClusterSize)), 20000)
    G, _ = adjacency_matrix_to_graph(adjacency_matrix)
    mst = nx.minimum_spanning_tree(G)
    edges = [e for e in mst.edges]
    bestPartition = None
    bestPartitionScore = float('-inf')
    numImprovements = 0
    for j in range(attempts):
        tree = mst.copy()
        edgesCopy = edges.copy()
        for j in range(numClusters):
            e = random.choice(edgesCopy)
            edgesCopy.remove(e)
            u, v = e
            tree.remove_edge(u, v)
        components = [list(tree.subgraph(c).copy().nodes) for c in nx.connected_components(tree)]
        partitionScore = 0
        centers = []
        homesByComponents = []
        for component in components:
            if len(component) == 1:
                partitionScore = float('-inf')
                break
            if len(component) >= 2 * avergaeClusterSize:
                partitionScore = float('-inf')
                break
            center = None
            bestCandidateScore = float('-inf')
            homesInComponent = [h for h in home_indices if h in component]
            homesByComponents.append(homesInComponent)
            for centerCandidate in component:    
                score = 0
                for h in homesInComponent:
                    score -= shortest[centerCandidate][h] ** 2 / len(homesInComponent)
                    if score < bestCandidateScore:
                        break
                if score > bestCandidateScore:
                    bestCandidateScore = score
                    center = centerCandidate
            partitionScore += bestCandidateScore
            centers.append(center)
        if partitionScore > bestPartitionScore:
            bestPartitionScore = partitionScore
            bestPartition = (centers, components, homesByComponents)
            numImprovements += 1
    if bestPartitionScore > float('-inf'):
        print('Partition sucessful with {} improvements'.format(numImprovements))
        return bestPartition
    else:
        return findPartition(home_indices, adjacency_matrix, numClusters, shortest)


def getShortestDistances(adjacency_matrix):
    G, _ = adjacency_matrix_to_graph(adjacency_matrix)
    return dict(nx.all_pairs_dijkstra_path_length(G))

@timeout(5)
def aStarSearchTour(problem, heuristic=lambda x,y: 0):
    """Search the node that has the lowest combined cost and heuristic first."""
    
    closed = set()
    fringe = utils.PriorityQueue()
    start_state = problem.getStartState()
    fringe.update(start_state, 0)
    parent_map = {}
    cost_map = {start_state: 0}

    def build_solution(state, start_state):
        path = []
        start_index = start_state[0]
        while state != start_state:
            cur_index = state[0]
            path.append(cur_index)
            state = parent_map[state]
        path.append(start_index)
        path.reverse()
        return path
    
    while not fringe.isEmpty():
        cur_state = fringe.pop()
        #print('explore' + str(cur_state))
        if problem.isGoalState(cur_state):
            return build_solution(cur_state, start_state)
        if cur_state not in closed:
            closed.add(cur_state)
            successors = problem.getSuccessors(cur_state)
            for next_state, action_cost in problem.getSuccessors(cur_state):
                new_cost = cost_map[cur_state] + action_cost
                if next_state not in parent_map.keys() or new_cost < cost_map[next_state]:
                    parent_map[next_state] = cur_state
                    cost_map[next_state] = new_cost
                    fringe.update(next_state, new_cost + heuristic(next_state, problem))
    print('aStarSearchTour counld not find solution')
    exit(1)

def minTour(locations, adjacency_matrix, start_index):
    problem = MinTourProblem(adjacency_matrix, locations, start_index)
    return aStarSearchTour(problem, maxDistanceHeuristic)

def makeLocalAdjacencyMatrix(locations, adjacency_matrix):
    numLocations = len(locations)
    localAdjacencyMatrix = []
    for i in range(numLocations):
        localAdjacencyMatrix.append([])
        for j in range(i):
            localAdjacencyMatrix[i].append(adjacency_matrix[locations[i]][locations[j]])
        localAdjacencyMatrix[i].append('x')
    for i in range(numLocations):
        for j in range(i+1, numLocations):
            localAdjacencyMatrix[i].append(localAdjacencyMatrix[j][i])
    return localAdjacencyMatrix


def GetGlobalRepresentation(localIndexMap, localCarPath, localDropoffMapping):
    globalCarPath = []
    globalDropoffMapping = {}
    for localIndex in localCarPath:
        globalCarPath.append(localIndexMap[localIndex])
    for localIndex in localDropoffMapping:
        globalDropoffMapping[localIndexMap[localIndex]] = [localIndexMap[localHomeIndex] for localHomeIndex  in localDropoffMapping[localIndex]]
    return globalCarPath, globalDropoffMapping 


def getNeighbour(num_locations, adjacency_matrix):
    neighbour = [[] for i in range(num_locations)]
    for i in range(num_locations):
        for j in range(num_locations):
            if adjacency_matrix[i][j] != 'x':
                neighbour[i].append(j)
    return neighbour


def solveWithRandom(list_of_locations, list_of_homes, starting_car_location, adjacency_matrix):
    neighbour = getNeighbour(len(list_of_locations), adjacency_matrix)
    home_indices = [list_of_locations.index(home) for home in list_of_homes]
    start_index = list_of_locations.index(starting_car_location)
    cur_index = start_index
    car_path = []
    dropoff_mapping = {}
    while home_indices or cur_index != start_index:
        car_path.append(cur_index)
        next_index = random.choice(neighbour[cur_index])
        numToDrop = int(len(home_indices) * random.random() + 0.5)
        for i in range(numToDrop):
            drop = random.choice(home_indices)
            if not cur_index in dropoff_mapping:
                dropoff_mapping[cur_index] = []
            dropoff_mapping[cur_index].append(drop)
            home_indices.remove(drop)
        cur_index = next_index
    car_path.append(start_index)
    return car_path, dropoff_mapping

def solveWithAStar(list_of_locations, list_of_homes, starting_car_location, adjacency_matrix, numNearbyHomes):
    home_indices = [list_of_locations.index(home) for home in list_of_homes]
    start_index = list_of_locations.index(starting_car_location)
    problem = DriveTAsHomeProblem(adjacency_matrix, home_indices, start_index, numNearbyHomes)
    car_path, dropoff_mapping = aStarSearch(problem, maxDistanceHeuristic)
    return car_path, dropoff_mapping

def aStarSearch(problem, heuristic=lambda x,y: 0):
    """Search the node that has the lowest combined cost and heuristic first."""
    
    closed = set()
    fringe = utils.PriorityQueue()
    start_state = problem.getStartState()
    fringe.update(start_state, 0)
    parent_map = {}
    cost_map = {start_state: 0}

    def build_solution(state, start_state):
        car_path = []
        dropoff_mapping = {}
        dropoff = None
        start_index = start_state[0]
        while state != start_state:
            cur_index = state[0]
            car_path.append(cur_index)
            if dropoff:
                if cur_index not in dropoff_mapping:
                    dropoff_mapping[cur_index] = []
                dropoff_mapping[cur_index].extend(dropoff)
            dropoff = parent_map[state][1]
            state = parent_map[state][0]
        car_path.append(start_index)
        if dropoff:
            if start_index not in dropoff_mapping:
                dropoff_mapping[start_index] = []
            dropoff_mapping[start_index].extend(dropoff)
        car_path.reverse()
        return car_path, dropoff_mapping
    while not fringe.isEmpty():
        cur_state = fringe.pop()
        #print('explore' + str(cur_state))
        if problem.isGoalState(cur_state):
            return build_solution(cur_state, start_state)
        if cur_state not in closed:
            closed.add(cur_state)
            successors = problem.getSuccessors(cur_state)
            for next_triple in problem.getSuccessors(cur_state):
                next_state = next_triple[0]
                dropoff = next_triple[1]
                new_cost = cost_map[cur_state] + next_triple[2]
                if next_state not in parent_map.keys() or new_cost < cost_map[next_state]:
                    parent_map[next_state] = (cur_state, dropoff)
                    cost_map[next_state] = new_cost
                    fringe.update(next_state, new_cost + heuristic(next_state, problem))
    print('aStarSearch counld not find solution')
    exit(1)

class DriveTAsHomeProblem(utils.SearchProblem):
    def __init__(self, adjacency_matrix, home_indices, start_index, numNearbyHomes):
        self.adjacency_matrix = adjacency_matrix
        self.G, _ = adjacency_matrix_to_graph(self.adjacency_matrix)
        self.home_indices = tuple(home_indices)
        self.start_index = start_index
        self.num_locations = len(adjacency_matrix)
        self.neighbour = self.getNeighbour()
        self.shortest = self.getShortestDistances()
        self.numNearbyHomes = int(numNearbyHomes)

    def getStartState(self):
        return (self.start_index, self.home_indices)

    def isGoalState(self, state):
        return state[0] == self.start_index and not state[1]

    def getSuccessors(self, state):
        successors = []
        cur_index = state[0]
        homes_left = state[1]
        nearby_homes = self.getNearbyHomes(state, self.numNearbyHomes)
        drop_off_options = list(powerset(nearby_homes))
        for next_index in self.neighbour[cur_index]:
            for drop_off in drop_off_options:
                homes_after_drop = tuple([h for h in homes_left if h not in drop_off])
                cost = 2 / 3 * self.shortest[cur_index][next_index]
                for h in drop_off:
                    cost += self.shortest[cur_index][h]
                successors.append(((next_index, homes_after_drop), drop_off, cost))
        return successors

    def getShortestDistances(self):
        return dict(nx.all_pairs_dijkstra_path_length(self.G))

    def getNearbyHomes(self, state, n):
        homes = list(state[1])
        if homes:
            homes.sort(key=lambda h: self.shortest[state[0]][h])
        return homes[0:n]

    def getNeighbour(self):
        neighbour = [[] for i in range(self.num_locations)]
        for i in range(self.num_locations):
            for j in range(self.num_locations):
                if self.adjacency_matrix[i][j] != 'x':
                    neighbour[i].append(j)
        return neighbour

    def getCostOfActions(self, actions):
        cost = 0
        for action in actions:
            cost += action[2]
        return cost

class MinTourProblem(utils.SearchProblem):
    def __init__(self, adjacency_matrix, targets, start_index):
        self.adjacency_matrix = adjacency_matrix
        self.G, _ = adjacency_matrix_to_graph(self.adjacency_matrix)
        self.targets = tuple(targets)
        self.start_index = start_index
        self.num_locations = len(adjacency_matrix)
        self.neighbour = self.getNeighbour()
        self.shortest = self.getShortestDistances()

    def getStartState(self):
        return (self.start_index, self.targets)

    def isGoalState(self, state):
        return state[0] == self.start_index and not state[1]

    def getSuccessors(self, state):
        successors = []
        cur_index = state[0]
        targets = state[1]
        for next_index in self.neighbour[cur_index]:
            targets_left = tuple([t for t in targets if t != cur_index])
            cost = 2 / 3 * self.shortest[cur_index][next_index]
            successors.append(((next_index, targets_left), cost))
        return successors

    def getShortestDistances(self):
        return dict(nx.all_pairs_dijkstra_path_length(self.G))

    def getNeighbour(self):
        neighbour = [[] for i in range(self.num_locations)]
        for i in range(self.num_locations):
            for j in range(self.num_locations):
                if self.adjacency_matrix[i][j] != 'x':
                    neighbour[i].append(j)
        return neighbour

    def getCostOfActions(self, actions):
        cost = 0
        for action in actions:
            cost += action[1]
        return cost    


def powerset(iterable):
    "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s)+1))

def maxDistanceHeuristic(state, problem):
    """
    A heuristic function estimates the cost from the current state to the nearest
    goal in the provided SearchProblem.  This heuristic is trivial.
    """
    targets_left = state[1]
    drivingCost = 2 / 3
    return max(problem.shortest[state[0]][problem.start_index], max([problem.shortest[state[0]][h] for h in targets_left]) * drivingCost if targets_left else 0)


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

