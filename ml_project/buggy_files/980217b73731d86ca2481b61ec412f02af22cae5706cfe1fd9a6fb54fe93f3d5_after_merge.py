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
            def cast_variables(arg, arg_name):
                warnings.warn(
                    f'Argument {arg_name} given as xarray Variable...casting to its data. '
                    'xarray DataArrays are recommended instead.'
                )
                return arg.data
            _mutate_arguments(bound_args, xr.Variable, cast_variables)

            # Obtain proper match if referencing an input
            match = list(wrap_like) if isinstance(wrap_like, tuple) else wrap_like
            if isinstance(wrap_like, str):
                match = bound_args.arguments[wrap_like]
            elif isinstance(wrap_like, tuple):
                for i, arg in enumerate(wrap_like):
                    if isinstance(arg, str):
                        match[i] = bound_args.arguments[arg]

            # Cast all DataArrays to Pint Quantities
            _mutate_arguments(bound_args, xr.DataArray, lambda arg, _: arg.metpy.unit_array)

            # Optionally cast all Quantities to their magnitudes
            if to_magnitude:
                _mutate_arguments(bound_args, units.Quantity, lambda arg, _: arg.m)

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