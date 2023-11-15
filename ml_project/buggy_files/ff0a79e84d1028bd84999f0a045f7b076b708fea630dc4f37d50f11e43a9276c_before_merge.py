def recalculate_single_worm_control_points(all_labels, ncontrolpoints):
    '''Recalculate the control points for labeled single worms
    
    Given a labeling of single worms, recalculate the control points
    for those worms.
    
    all_labels - a sequence of label matrices
    
    ncontrolpoints - the # of desired control points
    
    returns a two tuple:
    
    an N x M x 2 array where the first index is the object number,
    the second index is the control point number and the third index is 0
    for the Y or I coordinate of the control point and 1 for the X or J
    coordinate.
    
    a vector of N lengths.
    '''
    
    all_object_numbers = [ filter((lambda n: n > 0), np.unique(l))
                           for l in all_labels]
    module = UntangleWorms()
    module.create_settings()
    module.num_control_points.value = ncontrolpoints
    #
    # Put the module in training mode - assumes that the training file is
    # not present.
    #
    module.mode.value = MODE_TRAIN
    
    nobjects = np.max(np.hstack(all_object_numbers))
    result = np.ones((nobjects, ncontrolpoints, 2)) * np.nan
    lengths = np.zeros(nobjects)
    for object_numbers, labels in zip(all_object_numbers, all_labels):
        for object_number in object_numbers:
            mask = (labels == object_number)
            skeleton = morph.skeletonize(mask)
            graph = module.get_graph_from_binary(mask, skeleton)
            path_coords, path = module.get_longest_path_coords(
                graph, np.iinfo(int).max)
            if len(path_coords) == 0:
                # return NaN for the control points
                continue
            cumul_lengths = module.calculate_cumulative_lengths(path_coords)
            if cumul_lengths[-1] == 0:
                continue
            control_points = module.sample_control_points(
                path_coords, cumul_lengths, ncontrolpoints)
            result[(object_number-1), :, :] = control_points
            lengths[object_number-1] = cumul_lengths[-1]
    return result, lengths