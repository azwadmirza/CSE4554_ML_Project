    def wrapper(*args, **kwargs):
        bound_args = signature(func).bind(*args, **kwargs)
        bound_args.apply_defaults()

        # Fill in vertical_dim
        if 'vertical_dim' in bound_args.arguments:
            a = next(dataarray_arguments(bound_args), None)
            if a is not None:
                try:
                    bound_args.arguments['vertical_dim'] = a.metpy.find_axis_number('vertical')
                except AttributeError:
                    # If axis number not found, fall back to default but warn.
                    warnings.warn(
                        'Vertical dimension number not found. Defaulting to initial dimension.'
                    )

        return func(*bound_args.args, **bound_args.kwargs)