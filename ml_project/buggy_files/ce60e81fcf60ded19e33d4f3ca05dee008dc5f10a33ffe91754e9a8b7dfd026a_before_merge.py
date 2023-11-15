def expand_components(block):
    """
    Loop over block components and try expanding them. If expansion fails
    then save the component and try again later. This function has some
    built-in robustness for block-hierarchical models with circular
    references but will not work for all cases.
    """

    expansion_map = ComponentMap()
    redo_expansion = list()

    # Identify components that need to be expanded and try expanding them
    for c in block.component_objects(descend_into=True,
                                     sort=SortComponents.declOrder):
        try:
            update_contset_indexed_component(c, expansion_map)
        except AttributeError:
            redo_expansion.append(c)

    print('Completed first discretization pass')

    N = len(redo_expansion)
    print('Number of components to re-expand: ', N)
    while N:
        print(redo_expansion)
        for i in range(N):
            c = redo_expansion.pop()
            print('Re-expanding component ', str(c))
            expansion_map[c](c)
            # try:
            #     expansion_map[c](c)
            # except AttributeError:
            #     redo_expansion.append(c)
        print(redo_expansion)
        if len(redo_expansion) == N:
            raise DAE_Error("Unable to fully discretize %s. Possible "
                            "circular references detected between components "
                            "%s. Reformulate your model to remove circular "
                            "references or apply a discretization "
                            "transformation before linking blocks together."
                            %(block, str(redo_expansion)))
        N = len(redo_expansion)