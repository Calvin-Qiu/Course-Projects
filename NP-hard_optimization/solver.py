import os
import sys
sys.path.append('..')
sys.path.append('../..')
import argparse
import utils
import copy

# from timeout import timeout
from student_utils import *
from itertools import chain, combinations
import networkx as nx
import random
import scipy
import datetime
import time
import timeout_decorator
from tsp_solver.greedy import solve_tsp

"""
======================================================================
  Complete the following function.
======================================================================
"""

@timeout_decorator.timeout(360, timeout_exception=StopIteration)
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
            numNearbyHomes = int(params[1])
            return solveWithClusters(list_of_locations, list_of_homes, starting_car_location, adjacency_matrix, numNearbyHomes)
        if params[0] == 'astar':
            numNearbyHomes = int(params[1])
            return solveWithAStar(list_of_locations, list_of_homes, starting_car_location, adjacency_matrix, numNearbyHomes)
        if params[0] == 'random':
            return solveWithRandom(list_of_locations, list_of_homes, starting_car_location, adjacency_matrix)
        # if params[0] == 'greedy':
        #     return solveWithGreedy(list_of_locations, list_of_homes, starting_car_location, adjacency_matrix)


def solveWithClusters(list_of_locations, list_of_homes, starting_car_location, adjacency_matrix, numNearbyHomes):
    solver = KClutserSolver(list_of_locations, list_of_homes, starting_car_location, adjacency_matrix, numNearbyHomes)
    return solver.solve()


class KClutserSolver():
    def __init__(self, list_of_locations, list_of_homes, starting_car_location, adjacency_matrix, numNearbyHomes):
        # Represents everything by index
        self.locations = range(len(list_of_locations))
        self.homes = [list_of_locations.index(home) for home in list_of_homes]
        self.start = list_of_locations.index(starting_car_location)
        self.adjacencyMatrix = adjacency_matrix
        self.numNearbyHomes = numNearbyHomes
        self.G, _ = adjacency_matrix_to_graph(self.adjacencyMatrix)
        self.shortestDistances = dict(nx.all_pairs_dijkstra_path_length(self.G))
        self.k = (len(self.homes) // 5) + 1 # number of clusters
        self.shortestPaths = dict(nx.all_pairs_dijkstra_path(self.G, weight='weight'))
        self.effectiveAdjacencyMatrix, self.pathMatrix = self.getEffectiveAjacencyAndPathMatrix(self.adjacencyMatrix)
    
    def getKClusters(self):
        """ 
        Returns a list of clusters, where each cluster is a tuple (C, L, H), 
        where C is a list of centers, L is a list of locations in the cluster, and H is a list of homes in the cluster
        """
        bestClusters = None
        bestScore = float('inf')
        for j in range(len(self.homes)):
            homesLeft = self.homes.copy()
            centers = [] # a list of homes as centers
            for i in range(self.k):
                nextCenter = None
                if i == 0:
                    nextCenter = self.homes[j]
                else:
                    minDistances = [(home, min([self.shortestDistances[home][center] for center in centers])) for home in homesLeft] 
                    nextCenter = max(minDistances, key=lambda x: x[1])[0]
                centers.append(nextCenter)
                homesLeft.remove(nextCenter)
            homesByCluster = [[] for center in centers]
            locationsByCluster = [[] for center in centers]
            self.homesByCluster = homesByCluster
            self.locationsByCluster = locationsByCluster
            for home in self.homes:
                distances = [(center, self.shortestDistances[home][center]) for center in centers]
                distances.sort(key=lambda x: x[1])
                isCenter = distances[0][1] == 0
                closestCenters = [x[0] for x in distances]
                for center in closestCenters:
                    clusterIndex = centers.index(center)
                    if len(homesByCluster[clusterIndex]) < 7 or isCenter:
                        homesByCluster[clusterIndex].append(home)
                        break
            score = self.getScore(centers, homesByCluster)
            if score < bestScore:
                for i in range(len(homesByCluster)):
                    locations = [l for l in self.locations if l not in homesByCluster[i]]
                    #distancesToLocations = [(location, min([(h, self.shortestDistances[location][h]) for h in homesByCluster[i]])) for location in locations]
                    
                    distancesToLocations = [(location, self.shortestDistances[location][centers[i]]) for location in locations]
                    distancesToLocations.sort(key=lambda x: x[1])
                    locationsByCluster[i].extend(homesByCluster[i])
                    locationsByCluster[i].extend([x[0] for x in distancesToLocations[: 20]])
            
                bestClusters = [(centers[i], locationsByCluster[i], homesByCluster[i]) for i in range(len(centers))]
                bestScore = score
        for cluster in bestClusters:
            print(cluster[2])
        return bestClusters


    def getScore(self, centers, homesByCluster):
        score = sum([len(homesByCluster[i]) ** 2 for i in range(len(centers))])
        #score = max([len(homesByCluster[i]) for i in range(len(centers))])
        return score

    def solve(self):
        clusters = self.getKClusters()
        self.clusters = clusters
        centers = [cluster[0] for cluster in clusters]
        tourLocations = centers + [self.start] if self.start not in centers else centers
        print('Found clusters at {}'.format(datetime.datetime.now()))
        outerTour = self.getTour(self.start, tourLocations)
        print('Found tour through clusters at {}'.format(datetime.datetime.now()))
        numIter = 0
        componentPaths = []
        dropoffMapping = {}
        for center, locations, homes in clusters:
            subCarPath, subDropoffMapping = self.getPathInCluster(center, locations, homes, center, center)
            componentPaths.append(subCarPath)
            dropoffMapping.update(subDropoffMapping)
            print('{}-th subtour found at {}'.format(numIter, datetime.datetime.now()))
            numIter += 1
        completePath = []
        
        completePath = [self.start]
        if self.start in centers:
            completePath.extend(componentPaths[centers.index(self.start)][1:])
        last = self.start
        for cur in outerTour[1:-1]:
            completePath.extend(self.pathMatrix[last][cur][1:])
            completePath.extend(componentPaths[centers.index(cur)][1:])
            last = cur
        completePath.extend(self.pathMatrix[last][self.start][1:])
        # cleanPath = [completePath[0]]
        # for i in range(1, len(completePath)):
        #     if completePath[i] != completePath[i-1]:
        #         cleanPath.append(completePath[i])
        # print(cleanPath)
        print(completePath)
        # completePath = collapse(completePath, dropoffMapping)
        return completePath, dropoffMapping




    def getEffectiveAjacencyAndPathMatrix(self, adjacencyMatrix):
        """ Get the effective overall adjacency matrix defined by pairwise shortest path lengths
        """
        dim = range(len(adjacencyMatrix))
        effectiveAdjacencyMatrix = [[-1 for j in dim] for i in dim]
        pathMatrix = [[-1 for j in dim] for i in dim]
        for i in range(len(adjacencyMatrix)):
            for j in range(len(adjacencyMatrix)):
                effectiveAdjacencyMatrix[i][j] = self.shortestDistances[i][j]
                pathMatrix[i][j] = self.shortestPaths[i][j]
        return effectiveAdjacencyMatrix, pathMatrix


    def getClusterAdjancyAndPathMatrix(self, clusters):
        """ Returns the effective adjacency matrix and path matrix among the clusters and the starting point, 
            where A[i][j] is the distance between the i-th and j-th cluster and P[i][j] is the path that achive this distance
        """
        adjacencyMatrix = [[float('inf') for j in range(len(clusters))] for i in range(len(clusters))]
        pathMatrix = [[ None for j in range(len(clusters))] for i in range(len(clusters))]
        for i in range(len(clusters)):
            for j in range(len(clusters)):
                for h1 in clusters[i][1]:
                    for h2 in clusters[j][1]:
                        if self.shortestDistances[h1][h2] < adjacencyMatrix[i][j]:
                            adjacencyMatrix[i][j] = self.shortestDistances[h1][h2]
                            pathMatrix[i][j] = self.shortestPaths[h1][h2]
        return adjacencyMatrix, pathMatrix

    # def makeLocalAdjacencyMatrix(locations, adjancyMatrix):
    #     numLocations = len(locations)
    #     localAdjacencyMatrix = []
    #     for i in range(numLocations):
    #         localAdjacencyMatrix.append([])
    #         for j in range(i):
    #             localAdjacencyMatrix[i].append(adjancyMatrix[locations[i]][locations[j]])
    #         localAdjacencyMatrix[i].append('x')
    #     for i in range(numLocations):
    #         for j in range(i+1, numLocations):
    #             localAdjacencyMatrix[i].append(localAdjacencyMatrix[j][i])
    #     return localAdjacencyMatrix


    def getTour(self, start, targets):
        """ Solve the tour with TSP
        """
        tourAdjancyMatrix = self.makeLocalAdjacencyMatrix(targets)
        tourIndexMap = self.getLocalIndexMap(targets)
        startIndex = targets.index(start)
        bestTourCost = float('inf')
        bestTour = None
        for endIndex in range(len(tourAdjancyMatrix)):
            if endIndex != startIndex:
                tour = solve_tsp(tourAdjancyMatrix, endpoints = (startIndex, endIndex))
                tour.append(startIndex)
                cost = 0
                lastIndex = startIndex
                for nextIndex in tour[1:]:
                    cost += tourAdjancyMatrix[lastIndex][nextIndex]
                    lastIndex = nextIndex
                if cost < bestTourCost:
                    bestTourCost = cost
                    bestTour = tour
        return [tourIndexMap[x] for x in bestTour]
        
    def getPathInCluster(self, center, locations, homes, start, end):
        """ Get the path in cluster that drops off all homes that starts at start and ends at end """
        localAdjacencyMatrix = self.makeLocalAdjacencyMatrix(locations)
        localIndexMap = self.getLocalIndexMap(locations)
        localHomeIndicies = [locations.index(h) for h in homes] # home indicies in local coordinates
        localStartIndex = locations.index(start)
        localEndIndex = locations.index(end)
        localCenterIndex = locations.index(center)
        problem = DriveTAsHomeProblem(localCenterIndex, localAdjacencyMatrix, localHomeIndicies, localStartIndex, localEndIndex, self.numNearbyHomes)
        print('Search for subtour at, {}'.format(datetime.datetime.now()))
        localCarPath, localDropoffMapping = aStarSearch(problem, maxDistanceHeuristic)
        globalCarPath, globalDropoffMapping = self.getGlobalRepresentation(localIndexMap, localCarPath, localDropoffMapping)
        return globalCarPath, globalDropoffMapping
        

    def getLocalIndexMap(self, locations):
        localIndexMap = {}
        for i in range(len(locations)):
            localIndexMap[i] = locations[i] # i -> index of the i-th location in the cluster in the original graph
        return localIndexMap

    def makeLocalAdjacencyMatrix(self, locations):
        numLocations = len(locations)
        localAdjacencyMatrix = []
        for i in range(numLocations):
            localAdjacencyMatrix.append([])
            for j in range(i):
                localAdjacencyMatrix[i].append(self.effectiveAdjacencyMatrix[locations[i]][locations[j]])
            localAdjacencyMatrix[i].append('x')
        for i in range(numLocations):
            for j in range(i+1, numLocations):
                localAdjacencyMatrix[i].append(localAdjacencyMatrix[j][i])
        return localAdjacencyMatrix

    def getGlobalRepresentation(self, localIndexMap, localCarPath, localDropoffMapping):
        if localCarPath:
            globalCarPath = [localIndexMap[localCarPath[0]]]
            globalDropoffMapping = {}
            for i in range(len(localCarPath)):
                localIndex = localCarPath[i]
                if i < len(localCarPath) - 1:
                    globalCurIndex = localIndexMap[localIndex]
                    globalNextIndex = localIndexMap[localCarPath[i+1]]
                    if globalCurIndex != globalNextIndex:
                        globalCarPath.extend((self.pathMatrix[globalCurIndex][globalNextIndex][1:]))
            for localIndex in localDropoffMapping:
                globalDropoffMapping[localIndexMap[localIndex]] = [localIndexMap[localHomeIndex] for localHomeIndex  in localDropoffMapping[localIndex]]
            print(globalCarPath)
            return globalCarPath, globalDropoffMapping 
        else:
            localCenterIndex = list(localDropoffMapping.keys())[0]
            globalCenter = localIndexMap[localCenterIndex]
            return [], {globalCenter: [localIndexMap[localHomeIndex] for localHomeIndex  in localDropoffMapping[localCenterIndex]]}

class DriveTAsHomeProblem(utils.SearchProblem):
    def __init__(self, center_index, adjacency_matrix, home_indices, start_index, end_index, numNearbyHomes):
        self.center_index = center_index
        self.adjacency_matrix = adjacency_matrix
        self.G, _ = adjacency_matrix_to_graph(self.adjacency_matrix)
        self.home_indices = tuple(home_indices)
        self.start_index = start_index
        self.end_index = end_index
        self.num_locations = len(adjacency_matrix)
        self.neighbour = self.getNeighbour()
        self.shortest = self.getShortestDistances()
        self.numNearbyHomes = int(numNearbyHomes)
        self.isSingular = len(adjacency_matrix) == 1

    def getStartState(self):
        return (self.start_index, self.home_indices)

    def isGoalState(self, state):
        return state[0] == self.end_index and not state[1]

    def getSuccessors(self, state):
        successors = []
        cur_index = state[0]
        homes_left = state[1]
        nearby_homes = self.getNearbyHomes(state, self.numNearbyHomes)
        drop_off_options = list(powerset(nearby_homes))
        drop_off_options.append(list(homes_left))
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


def aStarSearch(problem, heuristic=lambda x,y: 0):
    """Search the node that has the lowest combined cost and heuristic first."""
    
    closed = set()
    fringe = utils.PriorityQueue()
    start_state = problem.getStartState()
    fringe.update(start_state, 0)
    parent_map = {}
    cost_map = {start_state: 0}
    start = time.time()

    def build_solution(state, start_state):
        if cost_map[state] > sum([problem.shortest[start_state[0]][h] for h in start_state[1]]):
            return giveUp(start_state)
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

    def giveUp(start_state):
        car_path = []
        dropoff_mapping = {}
        if list(start_state[1]):
            dropoff_mapping[start_state[0]] = list(start_state[1])
        print("Release at center")
        return car_path, dropoff_mapping

    if problem.isSingular:
        return giveUp(start_state)

    while not fringe.isEmpty():
        timeElapse = time.time() - start
        if timeElapse > 120:
            print("Time out")
            return giveUp(start_state)
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
    return drivingCost * max(problem.shortest[state[0]][problem.start_index], max([problem.shortest[state[0]][h] for h in targets_left]) if targets_left else 0)

def greedyHeuristic(state, problem):
    """
    A heuristic function estimates the cost from the current state to the nearest
    goal in the provided SearchProblem.  This heuristic is trivial.
    """
    targets_left = state[1]
    drivingCost = 2 / 3
    return drivingCost * (problem.shortest[state[0]][problem.start_index] ** 2 + sum([problem.shortest[state[0]][h] ** 2 for h in targets_left]) if targets_left else 0)

def collapse(path, drop_off):
    rept = {}
    l = 0
    for i in range(len(path)):
        if(not path[l] in rept):
            rept[path[l]] = l
        else:
            # handle cycle here
            prev = rept[path[l]]
            # if this entire path is a cycle, do nothing
            if prev == 0 and l == len(path) - 1:
                continue
            collapse_enabled = True
            for j in range(prev + 1, l):
                if (len(drop_off[path[j]]) != 0):
                    collapse_enabled = False
            if (not collapse_enabled):
                middle = collapse(path[prev:(l + 1)], drop_off)
                path = path[0:prev] + middle + path[l+1:]
            else:
                if (prev - 1 >= 0 and l + 1 < len(path) and path[prev - 1] == path[l+1] and len(drop_off[path[prev]]) == 0):
                    path = path[0:prev] + path[l+1:]
                else:
                    path = path[0:prev] + path[l:]
            l = prev - 1
        l += 1
    if (len(path) == 2 and path[0] == path[1]):
        return path[1:]
    return path


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


