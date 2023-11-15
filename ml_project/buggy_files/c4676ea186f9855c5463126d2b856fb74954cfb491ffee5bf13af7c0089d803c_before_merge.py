def draw_values(params, point=None, size=None):
    """
    Draw (fix) parameter values. Handles a number of cases:

        1) The parameter is a scalar
        2) The parameter is an *RV

            a) parameter can be fixed to the value in the point
            b) parameter can be fixed by sampling from the *RV
            c) parameter can be fixed using tag.test_value (last resort)

        3) The parameter is a tensor variable/constant. Can be evaluated using
        theano.function, but a variable may contain nodes which

            a) are named parameters in the point
            b) are *RVs with a random method

    """
    # Get fast drawable values (i.e. things in point or numbers, arrays,
    # constants or shares, or things that were already drawn in related
    # contexts)
    if point is None:
        point = {}
    with _DrawValuesContext() as context:
        params = dict(enumerate(params))
        drawn = context.drawn_vars
        evaluated = {}
        symbolic_params = []
        for i, p in params.items():
            # If the param is fast drawable, then draw the value immediately
            if is_fast_drawable(p):
                v = _draw_value(p, point=point, size=size)
                evaluated[i] = v
                continue

            name = getattr(p, 'name', None)
            if p in drawn:
                # param was drawn in related contexts
                v = drawn[p]
                evaluated[i] = v
            elif name is not None and name in point:
                # param.name is in point
                v = point[name]
                evaluated[i] = drawn[p] = v
            else:
                # param still needs to be drawn
                symbolic_params.append((i, p))

        if not symbolic_params:
            # We only need to enforce the correct order if there are symbolic
            # params that could be drawn in variable order
            return [evaluated[i] for i in params]

        # Distribution parameters may be nodes which have named node-inputs
        # specified in the point. Need to find the node-inputs, their
        # parents and children to replace them.
        leaf_nodes = {}
        named_nodes_parents = {}
        named_nodes_children = {}
        for _, param in symbolic_params:
            if hasattr(param, 'name'):
                # Get the named nodes under the `param` node
                nn, nnp, nnc = get_named_nodes_and_relations(param)
                leaf_nodes.update(nn)
                # Update the discovered parental relationships
                for k in nnp.keys():
                    if k not in named_nodes_parents.keys():
                        named_nodes_parents[k] = nnp[k]
                    else:
                        named_nodes_parents[k].update(nnp[k])
                # Update the discovered child relationships
                for k in nnc.keys():
                    if k not in named_nodes_children.keys():
                        named_nodes_children[k] = nnc[k]
                    else:
                        named_nodes_children[k].update(nnc[k])

        # Init givens and the stack of nodes to try to `_draw_value` from
        givens = {p.name: (p, v) for p, v in drawn.items()
                  if getattr(p, 'name', None) is not None}
        stack = list(leaf_nodes.values())  # A queue would be more appropriate
        while stack:
            next_ = stack.pop(0)
            if next_ in drawn:
                # If the node already has a givens value, skip it
                continue
            elif isinstance(next_, (tt.TensorConstant,
                                    tt.sharedvar.SharedVariable)):
                # If the node is a theano.tensor.TensorConstant or a
                # theano.tensor.sharedvar.SharedVariable, its value will be
                # available automatically in _compile_theano_function so
                # we can skip it. Furthermore, if this node was treated as a
                # TensorVariable that should be compiled by theano in
                # _compile_theano_function, it would raise a `TypeError:
                # ('Constants not allowed in param list', ...)` for
                # TensorConstant, and a `TypeError: Cannot use a shared
                # variable (...) as explicit input` for SharedVariable.
                continue
            else:
                # If the node does not have a givens value, try to draw it.
                # The named node's children givens values must also be taken
                # into account.
                children = named_nodes_children[next_]
                temp_givens = [givens[k] for k in givens if k in children]
                try:
                    # This may fail for autotransformed RVs, which don't
                    # have the random method
                    value = _draw_value(next_,
                                        point=point,
                                        givens=temp_givens,
                                        size=size)
                    givens[next_.name] = (next_, value)
                    drawn[next_] = value
                except theano.gof.fg.MissingInputError:
                    # The node failed, so we must add the node's parents to
                    # the stack of nodes to try to draw from. We exclude the
                    # nodes in the `params` list.
                    stack.extend([node for node in named_nodes_parents[next_]
                                  if node is not None and
                                  node.name not in drawn and
                                  node not in params])

        # the below makes sure the graph is evaluated in order
        # test_distributions_random::TestDrawValues::test_draw_order fails without it
        # The remaining params that must be drawn are all hashable
        to_eval = set()
        missing_inputs = set([j for j, p in symbolic_params])
        while to_eval or missing_inputs:
            if to_eval == missing_inputs:
                raise ValueError('Cannot resolve inputs for {}'.format([str(params[j]) for j in to_eval]))
            to_eval = set(missing_inputs)
            missing_inputs = set()
            for param_idx in to_eval:
                param = params[param_idx]
                if param in drawn:
                    evaluated[param_idx] = drawn[param]
                else:
                    try:  # might evaluate in a bad order,
                        value = _draw_value(param,
                                            point=point,
                                            givens=givens.values(),
                                            size=size)
                        evaluated[param_idx] = drawn[param] = value
                        givens[param.name] = (param, value)
                    except theano.gof.fg.MissingInputError:
                        missing_inputs.add(param_idx)

    return [evaluated[j] for j in params] # set the order back