def _draw_value(param, point=None, givens=None, size=None):
    """Draw a random value from a distribution or return a constant.

    Parameters
    ----------
    param : number, array like, theano variable or pymc3 random variable
        The value or distribution. Constants or shared variables
        will be converted to an array and returned. Theano variables
        are evaluated. If `param` is a pymc3 random variables, draw
        a new value from it and return that, unless a value is specified
        in `point`.
    point : dict, optional
        A dictionary from pymc3 variable names to their values.
    givens : dict, optional
        A dictionary from theano variables to their values. These values
        are used to evaluate `param` if it is a theano variable.
    size : int, optional
        Number of samples
    """
    if isinstance(param, (numbers.Number, np.ndarray)):
        return param
    elif isinstance(param, tt.TensorConstant):
        return param.value
    elif isinstance(param, tt.sharedvar.SharedVariable):
        return param.get_value()
    elif isinstance(param, (tt.TensorVariable, MultiObservedRV)):
        if point and hasattr(param, 'model') and param.name in point:
            return point[param.name]
        elif hasattr(param, 'random') and param.random is not None:
            return param.random(point=point, size=size)
        elif (hasattr(param, 'distribution') and
                hasattr(param.distribution, 'random') and
                param.distribution.random is not None):
            if hasattr(param, 'observations'):
                # shape inspection for ObservedRV
                dist_tmp = param.distribution
                try:
                    distshape = param.observations.shape.eval()
                except AttributeError:
                    distshape = param.observations.shape

                dist_tmp.shape = distshape
                try:
                    dist_tmp.random(point=point, size=size)
                except (ValueError, TypeError):
                    # reset shape to account for shape changes
                    # with theano.shared inputs
                    dist_tmp.shape = np.array([])
                    # We want to draw values to infer the dist_shape,
                    # we don't want to store these drawn values to the context
                    with _DrawValuesContextBlocker():
                        val = np.atleast_1d(dist_tmp.random(point=point,
                                                            size=None))
                    # Sometimes point may change the size of val but not the
                    # distribution's shape
                    if point and size is not None:
                        temp_size = np.atleast_1d(size)
                        if all(val.shape[:len(temp_size)] == temp_size):
                            dist_tmp.shape = val.shape[len(temp_size):]
                        else:
                            dist_tmp.shape = val.shape
                return dist_tmp.random(point=point, size=size)
            else:
                return param.distribution.random(point=point, size=size)
        else:
            if givens:
                variables, values = list(zip(*givens))
            else:
                variables = values = []
            # We only truly care if the ancestors of param that were given
            # value have the matching dshape and val.shape
            param_ancestors = \
                set(theano.gof.graph.ancestors([param],
                                               blockers=list(variables))
                    )
            inputs = [(var, val) for var, val in
                      zip(variables, values)
                      if var in param_ancestors]
            if inputs:
                input_vars, input_vals = list(zip(*inputs))
            else:
                input_vars = []
                input_vals = []
            func = _compile_theano_function(param, input_vars)
            if size is not None:
                size = np.atleast_1d(size)
            dshaped_variables = all((hasattr(var, 'dshape')
                                     for var in input_vars))
            if (values and dshaped_variables and
                not all(var.dshape == getattr(val, 'shape', tuple())
                        for var, val in zip(input_vars, input_vals))):
                output = np.array([func(*v) for v in zip(*input_vals)])
            elif (size is not None and any((val.ndim > var.ndim)
                  for var, val in zip(input_vars, input_vals))):
                output = np.array([func(*v) for v in zip(*input_vals)])
            else:
                output = func(*input_vals)
            return output
    raise ValueError('Unexpected type in draw_value: %s' % type(param))