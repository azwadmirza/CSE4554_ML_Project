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
                    if not bmin <= param.value <= bmax:
                        min_d = np.abs(param.value - bmin)
                        max_d = np.abs(param.value - bmax)
                        if min_d < max_d:
                            param.value = bmin
                        else:
                            param.value = bmax