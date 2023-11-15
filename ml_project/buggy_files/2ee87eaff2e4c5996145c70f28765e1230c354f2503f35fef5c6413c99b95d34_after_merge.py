    def ensure_parameters_in_bounds(self):
        """For all active components, snaps their free parameter values to
        be within their boundaries (if bounded). Does not touch the array of
        values.
        """
        for component in self:
            if component.active:
                for param in component.free_parameters:
                    bmin = -np.inf if param.bmin is None else param.bmin
                    bmax = np.inf if param.bmax is None else param.bmax
                    if param._number_of_elements == 1:
                        if not bmin <= param.value <= bmax:
                            min_d = np.abs(param.value - bmin)
                            max_d = np.abs(param.value - bmax)
                            if min_d < max_d:
                                param.value = bmin
                            else:
                                param.value = bmax
                    else:
                        values = np.array(param.value)
                        if param.bmin is not None:
                            minmask = values < bmin
                            values[minmask] = bmin
                        if param.bmax is not None:
                            maxmask = values > bmax
                            values[maxmask] = bmax
                        param.value = tuple(values)