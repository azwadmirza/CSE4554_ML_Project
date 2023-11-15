def _reproduce_stages(
    G, stages, node, downstream=False, ignore_build_cache=False, **kwargs
):
    r"""Derive the evaluation of the given node for the given graph.

    When you _reproduce a stage_, you want to _evaluate the descendants_
    to know if it make sense to _recompute_ it. A post-ordered search
    will give us an order list of the nodes we want.

    For example, let's say that we have the following pipeline:

                               E
                              / \
                             D   F
                            / \   \
                           B   C   G
                            \ /
                             A

    The derived evaluation of D would be: [A, B, C, D]

    In case that `downstream` option is specifed, the desired effect
    is to derive the evaluation starting from the given stage up to the
    ancestors. However, the `networkx.ancestors` returns a set, without
    any guarantee of any order, so we are going to reverse the graph and
    use a pre-ordered search using the given stage as a starting point.

                   E                                   A
                  / \                                 / \
                 D   F                               B   C   G
                / \   \        --- reverse -->        \ /   /
               B   C   G                               D   F
                \ /                                     \ /
                 A                                       E

    The derived evaluation of _downstream_ B would be: [B, D, E]
    """

    import networkx as nx

    if downstream:
        # NOTE (py3 only):
        # Python's `deepcopy` defaults to pickle/unpickle the object.
        # Stages are complex objects (with references to `repo`, `outs`,
        # and `deps`) that cause struggles when you try to serialize them.
        # We need to create a copy of the graph itself, and then reverse it,
        # instead of using graph.reverse() directly because it calls
        # `deepcopy` underneath -- unless copy=False is specified.
        pipeline = nx.dfs_preorder_nodes(G.copy().reverse(copy=False), node)
    else:
        pipeline = nx.dfs_postorder_nodes(G, node)

    result = []
    for n in pipeline:
        try:
            ret = _reproduce_stage(stages, n, **kwargs)

            if len(ret) != 0 and ignore_build_cache:
                # NOTE: we are walking our pipeline from the top to the
                # bottom. If one stage is changed, it will be reproduced,
                # which tells us that we should force reproducing all of
                # the other stages down below, even if their direct
                # dependencies didn't change.
                kwargs["force"] = True

            result += ret
        except Exception as ex:
            raise ReproductionError(stages[n].relpath, ex)
    return result