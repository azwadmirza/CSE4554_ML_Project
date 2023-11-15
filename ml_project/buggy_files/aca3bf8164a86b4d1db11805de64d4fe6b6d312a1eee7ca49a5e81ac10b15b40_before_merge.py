    def _sequence(self, extent, axis):
        """
        Determine whether the given extent can be sequenced along with
        all the extents of the source-cubes already registered with
        this :class:`_ProtoCube` into non-overlapping segments for the
        given axis.

        Args:

        * extent:
            The :class:`_CoordExtent` of the candidate source-cube.

        * axis:
            The candidate axis of concatenation.

        Returns:
            Boolean.

        """
        result = True

        # Add the new extent to the current extents collection.
        dim_extents = [skeleton.signature.dim_extents[axis]
                       for skeleton in self._skeletons]
        dim_extents.append(extent)

        # Sort into the appropriate dimension order.
        order = self._coord_signature.dim_order[axis]
        dim_extents.sort(reverse=(order == _DECREASING))

        # Ensure that the extents don't overlap.
        if len(dim_extents) > 1:
            for i, extent in enumerate(dim_extents[1:]):
                # Check the points - must be strictly monotonic.
                if order == _DECREASING:
                    left = dim_extents[i].points.min
                    right = extent.points.max
                else:
                    left = dim_extents[i].points.max
                    right = extent.points.min

                if left >= right:
                    result = False
                    break

                # Check the bounds - must be strictly monotonic.
                if extent.bounds is not None:
                    if order == _DECREASING:
                        left_0 = dim_extents[i].bounds[0].min
                        left_1 = dim_extents[1].bounds[1].min
                        right_0 = extent.bounds[0].max
                        right_1 = extent.bounds[1].max
                    else:
                        left_0 = dim_extents[i].bounds[0].max
                        left_1 = dim_extents[i].bounds[1].max
                        right_0 = extent.bounds[0].min
                        right_1 = extent.bounds[1].min

                    lower_bound_fail = left_0 >= right_0
                    upper_bound_fail = left_1 >= right_1

                    if lower_bound_fail or upper_bound_fail:
                        result = False
                        break

        return result