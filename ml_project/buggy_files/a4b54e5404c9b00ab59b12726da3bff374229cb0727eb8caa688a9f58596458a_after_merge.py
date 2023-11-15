    def wrapper(*args, **kwargs):
        bound_args = signature(func).bind(*args, **kwargs)
        bound_args.apply_defaults()

        # Search for DataArray with valid latitude and longitude coordinates to find grid
        # deltas and any other needed parameter
        dataarray_arguments = [
            value for value in bound_args.arguments.values()
            if isinstance(value, xr.DataArray)
        ]
        grid_prototype = None
        for da in dataarray_arguments:
            if hasattr(da.metpy, 'latitude') and hasattr(da.metpy, 'longitude'):
                grid_prototype = da
                break

        # Fill in x_dim/y_dim
        if (
            grid_prototype is not None
            and 'x_dim' in bound_args.arguments
            and 'y_dim' in bound_args.arguments
        ):
            try:
                bound_args.arguments['x_dim'] = grid_prototype.metpy.find_axis_number('x')
                bound_args.arguments['y_dim'] = grid_prototype.metpy.find_axis_number('y')
            except AttributeError:
                # If axis number not found, fall back to default but warn.
                warnings.warn('Horizontal dimension numbers not found. Defaulting to '
                              '(..., Y, X) order.')

        # Fill in vertical_dim
        if (
            grid_prototype is not None
            and 'vertical_dim' in bound_args.arguments
        ):
            try:
                bound_args.arguments['vertical_dim'] = (
                    grid_prototype.metpy.find_axis_number('vertical')
                )
            except AttributeError:
                # If axis number not found, fall back to default but warn.
                warnings.warn(
                    'Vertical dimension number not found. Defaulting to (..., Z, Y, X) order.'
                )

        # Fill in dz
        if (
            grid_prototype is not None
            and 'dz' in bound_args.arguments
            and bound_args.arguments['dz'] is None
        ):
            try:
                vertical_coord = grid_prototype.metpy.vertical
                bound_args.arguments['dz'] = np.diff(vertical_coord.metpy.unit_array)
            except (AttributeError, ValueError):
                # Skip, since this only comes up in advection, where dz is optional (may not
                # need vertical at all)
                pass

        # Fill in dx/dy
        if (
            'dx' in bound_args.arguments and bound_args.arguments['dx'] is None
            and 'dy' in bound_args.arguments and bound_args.arguments['dy'] is None
        ):
            if grid_prototype is not None:
                bound_args.arguments['dx'], bound_args.arguments['dy'] = (
                    grid_deltas_from_dataarray(grid_prototype, kind='actual')
                )
            elif 'dz' in bound_args.arguments:
                # Handle advection case, allowing dx/dy to be None but dz to not be None
                if bound_args.arguments['dz'] is None:
                    raise ValueError(
                        'Must provide dx, dy, and/or dz arguments or input DataArray with '
                        'proper coordinates.'
                    )
            else:
                raise ValueError('Must provide dx/dy arguments or input DataArray with '
                                 'latitude/longitude coordinates.')

        # Fill in latitude
        if 'latitude' in bound_args.arguments and bound_args.arguments['latitude'] is None:
            if grid_prototype is not None:
                bound_args.arguments['latitude'] = (
                    grid_prototype.metpy.latitude
                )
            else:
                raise ValueError('Must provide latitude argument or input DataArray with '
                                 'latitude/longitude coordinates.')

        return func(*bound_args.args, **bound_args.kwargs)