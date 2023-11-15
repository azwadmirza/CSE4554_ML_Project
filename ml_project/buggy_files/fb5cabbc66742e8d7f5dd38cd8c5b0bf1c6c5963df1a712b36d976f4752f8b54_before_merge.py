    def _get_indexers_coordinates(self, indexers):
        """  Extract coordinates from indexers.
        Returns an OrderedDict mapping from coordinate name to the
        coordinate variable.

        Only coordinate with a name different from any of self.variables will
        be attached.
        """
        from .dataarray import DataArray

        coord_list = []
        for k, v in indexers.items():
            if isinstance(v, DataArray):
                v_coords = v.coords
                if v.dtype.kind == 'b':
                    if v.ndim != 1:  # we only support 1-d boolean array
                        raise ValueError(
                            '{:d}d-boolean array is used for indexing along '
                            'dimension {!r}, but only 1d boolean arrays are '
                            'supported.'.format(v.ndim, k))
                    # Make sure in case of boolean DataArray, its
                    # coordinate also should be indexed.
                    v_coords = v[v.values.nonzero()[0]].coords

                coord_list.append({d: v_coords[d].variable for d in v.coords})

        # we don't need to call align() explicitly, because merge_variables
        # already checks for exact alignment between dimension coordinates
        coords = merge_variables(coord_list)

        for k in self.dims:
            # make sure there are not conflict in dimension coordinates
            if (k in coords and k in self._variables and
                    not coords[k].equals(self._variables[k])):
                raise IndexError(
                    'dimension coordinate {!r} conflicts between '
                    'indexed and indexing objects:\n{}\nvs.\n{}'
                    .format(k, self._variables[k], coords[k]))

        attached_coords = OrderedDict()
        for k, v in coords.items():  # silently drop the conflicted variables.
            if k not in self._variables:
                attached_coords[k] = v
        return attached_coords