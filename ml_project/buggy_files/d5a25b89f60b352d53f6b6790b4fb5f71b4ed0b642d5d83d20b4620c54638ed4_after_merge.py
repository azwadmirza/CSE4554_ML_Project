def expand_components(block):
    """
    Loop over block components and try expanding them. If expansion fails
    then save the component and try again later. This function has some
    built-in robustness for block-hierarchical models with circular
    references but will not work for all cases.
    """

    # expansion_map is used to map components to the functions used to
    # expand them so that the update_contset_indexed_component function
    # logic only has to be called once even in the case where we have to
    # re-try expanding components due to circular references
    expansion_map = ComponentMap()
    redo_expansion = list()

    # Record the missing BlockData before expanding components. This is for
    # the case where a ContinuousSet indexed Block is used in a Constraint.
    # If the Constraint is expanded before the Block then the missing
    # BlockData will be added to the indexed Block but will not be
    # constructed correctly.
    for blk in block.component_objects(Block, descend_into=True):
        missing_idx = set(blk._index) - set(iterkeys(blk._data))
        if missing_idx:
            blk._dae_missing_idx = missing_idx

    # Wrap this whole process in a try block in order to ensure that errors
    # swallowed by the LoggingIntercept context below are re-raised if the
    # discretization encounters an error it isn't expecting.
    try:

        # Intercept logging to suppress Error messages arising from failed
        # constraint rules. These error messages get logged even though the
        # AttributeError causing the error is caught and handled by this
        # function when expanding discretized models. We maintain a stream
        # of the intercepted logging messages which will be printed if an
        # unexpected exception is raised.
        buf = StringIO()
        with LoggingIntercept(buf, 'pyomo.core', logging.ERROR):

            # Identify components that need to be expanded and try expanding
            # them
            for c in block.component_objects(descend_into=True,
                                             sort=SortComponents.declOrder):
                try:
                    update_contset_indexed_component(c, expansion_map)
                except AttributeError:
                    redo_expansion.append(c)

            # Re-try expansion on any components that failed the first time.
            #  This is indicative of circular component references and not
            # expanding components in the correct order the first time
            # through.
            N = len(redo_expansion)
            while N:
                for i in range(N):
                    c = redo_expansion.pop()
                    try:
                        expansion_map[c](c)
                    except AttributeError:
                        redo_expansion.append(c)
                if len(redo_expansion) == N:
                    raise DAE_Error("Unable to fully discretize %s. Possible "
                                    "circular references detected between "
                                    "components %s. Reformulate your model to"
                                    " remove circular references or apply a "
                                    "discretization transformation before "
                                    "linking blocks together."
                                    % (block, str(redo_expansion)))

                N = len(redo_expansion)

    except Exception as e:
        logger.error(buf.getvalue())
        raise