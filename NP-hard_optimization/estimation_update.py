def update_estimation(dict_of_sp, array_of_sum_of_distances_to_all_homes, array_of_num_of_nearby_homes, new_weights,
                      starting_v):
    """
    :param dict_of_sp: dictionary of shortest paths between any two vertices in the graph
    :param array_of_sum_of_distances_to_all_homes: value at index i corresponds to the sum of all homes to vertex i
    :param array_of_num_of_nearby_homes: value at index i corresponds to the number of nearby homes
    :param new_weights: array of size 3
        1. distance from starting v to curr v
        2. sum of distances from curr v to all homes
        3. num of homes within a range
    :return: array of updated scores
    """
    num_of_v = len(array_of_num_of_nearby_homes)
    updated_scores = [0] * num_of_v
    for v in range(num_of_v):
        updated_scores[v] = new_weights[0] * dict_of_sp[(starting_v, v)] + \
                            new_weights[1] * array_of_sum_of_distances_to_all_homes[v] + \
                            new_weights[2] * array_of_num_of_nearby_homes[v]
    return updated_scores
