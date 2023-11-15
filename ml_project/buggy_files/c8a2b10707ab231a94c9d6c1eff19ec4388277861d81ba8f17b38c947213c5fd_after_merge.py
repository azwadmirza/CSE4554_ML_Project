    def _merge_raw(self, other):
        """For use with binary arithmetic."""
        if other is None:
            variables = OrderedDict(self.variables)
        else:
            # don't align because we already called xarray.align
            variables = merge_coords_without_align(
                [self.variables, other.variables])
        return variables