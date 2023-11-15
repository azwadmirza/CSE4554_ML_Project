def update_contset_indexed_component(comp, expansion_map):
    """
    Update any model components which are indexed by a ContinuousSet that
    has changed
    """

    # This implemenation will *NOT* check for or update
    # components which use a ContinuousSet implicitly. ex) an
    # objective function which iterates through a ContinuousSet and
    # sums the squared error.  If you use a ContinuousSet implicitly
    # you must initialize it with every index you would like to have
    # access to!

    if comp.type() is Suffix:
        return
    
    # Params indexed by a ContinuousSet should include an initialize
    # and/or default rule which will be called automatically when the
    # parameter value at a new point in the ContinuousSet is
    # requested. Therefore, no special processing is required for
    # Params.
    if comp.type() is Param:
        return

    # Components indexed by a ContinuousSet must have a dimension of at
    # least 1
    if comp.dim() == 0:
        return

    # Extract the indexing sets. Must treat components with a single
    # index separately from components with multiple indexing sets.
    if comp._implicit_subsets is None:
        indexset = [comp._index]
    else:
        indexset = comp._implicit_subsets

    for s in indexset:
        if s.type() == ContinuousSet and s.get_changed():
            if isinstance(comp, Var):  # Don't use the type() method here
                # because we want to catch DerivativeVar components as well
                # as Var components
                expansion_map[comp] = _update_var
                _update_var(comp)
            elif comp.type() == Constraint:
                expansion_map[comp] = _update_constraint
                _update_constraint(comp)
            elif comp.type() == Expression:
                expansion_map[comp] = _update_expression
                _update_expression(comp)
            elif isinstance(comp, Piecewise):
                expansion_map[comp] =_update_piecewise
                _update_piecewise(comp)
            elif comp.type() == Block:
                expansion_map[comp] = _update_block
                _update_block(comp)    
            else:
                raise TypeError(
                    "Found component %s of type %s indexed "
                    "by a ContinuousSet. Components of this type are "
                    "not currently supported by the automatic "
                    "discretization transformation in pyomo.dae. "
                    "Try adding the component to the model "
                    "after discretizing. Alert the pyomo developers "
                    "for more assistance." % (str(comp), comp.type()))