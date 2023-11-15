def get_tree_implementation_by_config_or_depth(extra_config, max_depth, low=3, high=10):
    """
    Utility function used to pick the tree implementation based on input parameters and heurstics.
    The current heuristic is such that GEMM <= low < PerfTreeTrav <= high < TreeTrav
    Args:
        max_depth: The maximum tree-depth found in the tree model.
        low: The maximum depth below which GEMM strategy is used
        high: The maximum depth for which PerfTreeTrav strategy is used

    Returns: A tree implementation
    """
    if constants.TREE_IMPLEMENTATION not in extra_config:
        if max_depth is not None and max_depth <= low:
            return TreeImpl.gemm
        elif max_depth is not None and max_depth <= high:
            return TreeImpl.perf_tree_trav
        else:
            return TreeImpl.tree_trav

    if extra_config[constants.TREE_IMPLEMENTATION] == TreeImpl.gemm.name:
        return TreeImpl.gemm
    elif extra_config[constants.TREE_IMPLEMENTATION] == TreeImpl.tree_trav.name:
        return TreeImpl.tree_trav
    elif extra_config[constants.TREE_IMPLEMENTATION] == TreeImpl.perf_tree_trav.name:
        return TreeImpl.perf_tree_trav
    else:
        raise MissingConverter("Tree implementation {} not found".format(extra_config))