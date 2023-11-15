    def _merge_inplace(self, other):
        """For use with in-place binary arithmetic."""
        if other is None:
            yield
        else:
            # don't include indexes in priority_vars, because we didn't align
            # first
            priority_vars = OrderedDict(
                (k, v) for k, v in self.variables.items() if k not in self.dims)
            variables = merge_coords_without_align(
                [self.variables, other.variables], priority_vars=priority_vars)
            yield
            self._update_coords(variables)