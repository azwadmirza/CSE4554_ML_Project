    def wrapper(*args, **kwargs):
        bound_args = signature(func).bind(*args, **kwargs)
        bound_args.apply_defaults()

        # Search for DataArray in arguments
        dataarray_arguments = [
            value for value in bound_args.arguments.values()
            if isinstance(value, xr.DataArray)
        ]

        # Fill in vertical_dim
        if (
            len(dataarray_arguments) > 0
            and 'vertical_dim' in bound_args.arguments
        ):
            try:
                bound_args.arguments['vertical_dim'] = (
                    dataarray_arguments[0].metpy.find_axis_number('vertical')
                )
            except AttributeError:
                # If axis number not found, fall back to default but warn.
                warnings.warn(
                    'Vertical dimension number not found. Defaulting to initial dimension.'
                )

        return func(*bound_args.args, **bound_args.kwargs)