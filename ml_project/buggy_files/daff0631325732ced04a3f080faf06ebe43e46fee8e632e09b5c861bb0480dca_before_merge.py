    def _scalar_plotting_units(scalar_value, plotting_units):
        """Handle conversion to plotting units for barbs and arrows."""
        if plotting_units:
            if hasattr(scalar_value, 'units'):
                scalar_value = scalar_value.to(plotting_units)
            else:
                raise ValueError('To convert to plotting units, units must be attached to '
                                 'scalar value being converted.')
        return scalar_value