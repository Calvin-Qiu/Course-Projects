"""
create estimate for each vertex v:
    1. (not in this file) distance from starting v to curr v
    2. sum of distances from curr v to all homes
    3. num of homes within a range

input:
    :param adj_matrix
"""


def nearby_homes(adj_matrix, dist_of_defined_nearness):
    """
    :param dist_of_defined_nearness: the distance that we consider to be "near" v
    :return array of arrays of homes nearby
    """
    homes_nearby = [[0 for col in range(len(adj_matrix))] for row in range(len(adj_matrix))]
    for v in range(len(adj_matrix)):
        for neighbor in range(len(adj_matrix)):
            if adj_matrix[v][neighbor] != 0:
                include_neighbor_in_each_depth(neighbor, v, 0, dist_of_defined_nearness, adj_matrix, homes_nearby)
    return homes_nearby


def include_neighbor_in_each_depth(curr_v, last_v, dist_to_last_v_depth, dist_of_defined_nearness, adj_matrix,
                                   homes_nearby):
    for neighbor in range(len(adj_matrix)):
        if (neighbor != last_v) and (homes_nearby[curr_v][neighbor] != 1):
            dist_from_last_to_curr = adj_matrix[curr_v][neighbor]
            if dist_to_last_v_depth + dist_from_last_to_curr <= dist_of_defined_nearness:
                homes_nearby[curr_v][neighbor] = 1
                homes_nearby[neighbor][curr_v] = 1
                include_neighbor_in_each_depth(neighbor, curr_v, dist_to_last_v_depth + dist_from_last_to_curr)


def array_of_sum_of_distances_to_all_homes(adj_matrix, array_of_home_indicator, dict_of_sp):
    """
    :param array_of_home_indicator: if vertex i is a home, array_of_home_indicator[i] = 1, otherwise = 0
    :param dict_of_sp: dictionary of shortest paths between any two vertices in the graph
    """
    array_of_sum_of_dist_to_all_homes = [0] * len(adj_matrix)
    for v in range(len(adj_matrix)):
        for u in range(len(adj_matrix)):
            if u != v:
                if array_of_home_indicator[u]:
                    array_of_sum_of_dist_to_all_homes[v] += dict_of_sp[(v, u)]
    return array_of_sum_of_dist_to_all_homes
