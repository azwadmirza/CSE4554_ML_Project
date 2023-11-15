    def register(self, cube, axis=None, error_on_mismatch=False,
                 check_aux_coords=False):
        """
        Determine whether the given source-cube is suitable for concatenation
        with this :class:`_ProtoCube`.

        Args:

        * cube:
            The :class:`iris.cube.Cube` source-cube candidate for
            concatenation.

        Kwargs:

        * axis:
            Seed the dimension of concatenation for the :class:`_ProtoCube`
            rather than rely on negotiation with source-cubes.

        * error_on_mismatch:
            If True, raise an informative error if registration fails.

        Returns:
            Boolean.

        """
        # Verify and assert the nominated axis.
        if axis is not None and self.axis is not None and self.axis != axis:
            msg = 'Nominated axis [{}] is not equal ' \
                'to negotiated axis [{}]'.format(axis, self.axis)
            raise ValueError(msg)

        # Check for compatible cube signatures.
        cube_signature = _CubeSignature(cube)
        match = self._cube_signature.match(cube_signature, error_on_mismatch)

        # Check for compatible coordinate signatures.
        if match:
            coord_signature = _CoordSignature(cube_signature)
            candidate_axis = self._coord_signature.candidate_axis(
                coord_signature)
            match = candidate_axis is not None and \
                (candidate_axis == axis or axis is None)

        # Check for compatible coordinate extents.
        if match:
            match = self._sequence(coord_signature.dim_extents[candidate_axis],
                                   candidate_axis)

        # Check for compatible AuxCoords.
        if match:
            if check_aux_coords:
                for coord_a, coord_b in zip(
                        self._cube_signature.aux_coords_and_dims,
                        cube_signature.aux_coords_and_dims):
                    # AuxCoords that span the candidate axis can difffer
                    if (candidate_axis not in coord_a.dims or
                            candidate_axis not in coord_b.dims):
                        if not coord_a == coord_b:
                            match = False

        if match:
            # Register the cube as a source-cube for this proto-cube.
            self._add_skeleton(coord_signature, cube.lazy_data())
            # Declare the nominated axis of concatenation.
            self._axis = candidate_axis

        if match:
            # If the protocube dimension order is constant (indicating it was
            # created from a cube with a length 1 dimension coordinate) but
            # a subsequently registered cube has a non-constant dimension
            # order we should use that instead of _CONSTANT to make sure all
            # the ordering checks and sorts work as expected.
            existing_order = self._coord_signature.dim_order[self.axis]
            this_order = coord_signature.dim_order[self.axis]
            if existing_order == _CONSTANT and this_order != _CONSTANT:
                self._coord_signature.dim_order[self.axis] = this_order

        return match