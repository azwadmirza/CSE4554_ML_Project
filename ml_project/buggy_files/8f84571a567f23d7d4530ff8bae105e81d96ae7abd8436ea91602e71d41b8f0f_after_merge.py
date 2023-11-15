def old_bound_to_new(bounds):
    """Convert the old bounds representation to the new one.

    The new representation is a tuple (lb, ub) and the old one is a list
    containing n tuples, ith containing lower and upper bound on a ith
    variable.
    If any of the entries in lb/ub are None they are replaced by
    -np.inf/np.inf.
    """
    lb, ub = zip(*bounds)
    lb = np.array([x if x is not None else -np.inf for x in lb])
    ub = np.array([x if x is not None else np.inf for x in ub])
    return lb, ub