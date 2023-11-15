def expand_variable_dicts(list_of_variable_dicts):
    # type: (List[Union[Dataset, Dict]]) -> List[Dict[Any, Variable]]
    """Given a list of dicts with xarray object values, expand the values.

    Parameters
    ----------
    list_of_variable_dicts : list of dict or Dataset objects
        The each value for the mappings must be of the following types:
        - an xarray.Variable
        - a tuple `(dims, data[, attrs[, encoding]])` that can be converted in
          an xarray.Variable
        - or an xarray.DataArray

    Returns
    -------
    A list of ordered dictionaries with all values given by those found on the
    original dictionaries or coordinates, all of which are xarray.Variable
    objects.
    """
    var_dicts = []

    for variables in list_of_variable_dicts:
        if hasattr(variables, 'variables'):  # duck-type Dataset
            sanitized_vars = variables.variables
        else:
            # append sanitized_vars before filling it up because we want coords
            # to appear afterwards
            sanitized_vars = OrderedDict()

            for name, var in variables.items():
                if hasattr(var, '_coords'):  # duck-type DataArray
                    # use private API for speed
                    coords = var._coords.copy()
                    # explicitly overwritten variables should take precedence
                    coords.pop(name, None)
                    var_dicts.append(coords)

                var = as_variable(var, name=name)
                sanitized_vars[name] = var

        var_dicts.append(sanitized_vars)

    return var_dicts