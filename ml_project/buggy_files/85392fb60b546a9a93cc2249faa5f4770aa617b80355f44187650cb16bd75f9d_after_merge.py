def matching_time_indices(stamps_1, stamps_2, max_diff=0.01, offset_2=0.0):
    """
    searches for the best matching timestamps of 2 lists and returns their list indices
    :param stamps_1: first vector of timestamps
    :param stamps_2: second vector of timestamps
    :param max_diff: max. allowed absolute time difference
    :param offset_2: optional offset of second vector
    :return: the indices of the matching stamps in stamps_1
    """
    matching_indices = []
    stamps_2 = copy.deepcopy(stamps_2)
    stamps_2 += offset_2
    for stamp in stamps_1:
        diffs = np.abs(stamps_2 - stamp)
        argmin = np.argmin(diffs)
        if diffs[argmin] <= max_diff:
            matching_indices.append(argmin)
    return matching_indices