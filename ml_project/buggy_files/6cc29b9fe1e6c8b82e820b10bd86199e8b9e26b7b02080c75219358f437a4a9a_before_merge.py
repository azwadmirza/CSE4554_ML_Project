def preprocess_and_wrap(broadcast=None, wrap_like=None, match_unit=False, to_magnitude=False):
    """Return decorator to wrap array calculations for type flexibility.

    Assuming you have a calculation that works internally with `pint.Quantity` or
    `numpy.ndarray`, this will wrap the function to be able to handle `xarray.DataArray` and
    `pint.Quantity` as well (assuming appropriate match to one of the input arguments).

    Parameters
    ----------
    broadcast : iterable of str or None
        Iterable of string labels for arguments to broadcast against each other using xarray,
        assuming they are supplied as `xarray.DataArray`. No automatic broadcasting will occur
        with default of None.
    wrap_like : str or array-like or tuple of str or tuple of array-like or None
        Wrap the calculation output following a particular input argument (if str) or data
        object (if array-like). If tuple, will assume output is in the form of a tuple,
        and wrap iteratively according to the str or array-like contained within. If None,
        will not wrap output.
    match_unit : bool
        If true, force the unit of the final output to be that of wrapping object (as
        determined by wrap_like), no matter the original calculation output. Defaults to
        False.
    to_magnitude : bool
        If true, downcast xarray and Pint arguments to their magnitude. If false, downcast
        xarray arguments to Quantity, and do not change other array-like arguments.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            bound_args = signature(func).bind(*args, **kwargs)

            # Auto-broadcast select xarray arguments, and update bound_args
            if broadcast is not None:
                arg_names_to_broadcast = tuple(
                    arg_name for arg_name in broadcast
                    if arg_name in bound_args.arguments
                    and isinstance(
                        bound_args.arguments[arg_name],
                        (xr.DataArray, xr.Variable)
                    )
                )
                broadcasted_args = xr.broadcast(
                    *(bound_args.arguments[arg_name] for arg_name in arg_names_to_broadcast)
                )
                for i, arg_name in enumerate(arg_names_to_broadcast):
                    bound_args.arguments[arg_name] = broadcasted_args[i]

            # Cast all Variables to their data and warn
            # (need to do before match finding, since we don't want to rewrap as Variable)
            for arg_name in bound_args.arguments:
                if isinstance(bound_args.arguments[arg_name], xr.Variable):
                    warnings.warn(
                        f'Argument {arg_name} given as xarray Variable...casting to its data. '
                        'xarray DataArrays are recommended instead.'
                    )
                    bound_args.arguments[arg_name] = bound_args.arguments[arg_name].data

            # Obtain proper match if referencing an input
            match = list(wrap_like) if isinstance(wrap_like, tuple) else wrap_like
            if isinstance(wrap_like, str):
                match = bound_args.arguments[wrap_like]
            elif isinstance(wrap_like, tuple):
                for i, arg in enumerate(wrap_like):
                    if isinstance(arg, str):
                        match[i] = bound_args.arguments[arg]

            # Cast all DataArrays to Pint Quantities
            for arg_name in bound_args.arguments:
                if isinstance(bound_args.arguments[arg_name], xr.DataArray):
                    bound_args.arguments[arg_name] = (
                        bound_args.arguments[arg_name].metpy.unit_array
                    )

            # Optionally cast all Quantities to their magnitudes
            if to_magnitude:
                for arg_name in bound_args.arguments:
                    if isinstance(bound_args.arguments[arg_name], units.Quantity):
                        bound_args.arguments[arg_name] = bound_args.arguments[arg_name].m

            # Evaluate inner calculation
            result = func(*bound_args.args, **bound_args.kwargs)

            # Wrap output based on match and match_unit
            if match is None:
                return result
            else:
                if match_unit:
                    wrapping = _wrap_output_like_matching_units
                else:
                    wrapping = _wrap_output_like_not_matching_units

                if isinstance(match, list):
                    return tuple(wrapping(*args) for args in zip(result, match))
                else:
                    return wrapping(result, match)
        return wrapper
    return decorator