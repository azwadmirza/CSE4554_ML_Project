    def get_vertex_centered_data(self, fields, smoothed=True, no_ghost=False):
        _old_api = isinstance(fields, (string_types, tuple))
        if _old_api:
            message = (
                'get_vertex_centered_data() requires list of fields, rather than '
                'a single field as an argument.'
            )
            warnings.warn(message, DeprecationWarning, stacklevel=2)
            fields = [fields]

        # Make sure the field list has only unique entries
        fields = list(set(fields))
        new_fields = {}
        for field in fields:
            finfo = self.ds._get_field_info(field)
            new_fields[field] = self.ds.arr(
                np.zeros(self.ActiveDimensions + 1), finfo.units)
        if no_ghost:
            for field in fields:
                # Ensure we have the native endianness in this array.  Avoid making
                # a copy if possible.
                old_field = np.asarray(self[field], dtype="=f8")
                # We'll use the ghost zone routine, which will naturally
                # extrapolate here.
                input_left = np.array([0.5, 0.5, 0.5], dtype="float64")
                output_left = np.array([0.0, 0.0, 0.0], dtype="float64")
                # rf = 1 here
                ghost_zone_interpolate(1, old_field, input_left,
                                       new_fields[field], output_left)
        else:
            cg = self.retrieve_ghost_zones(1, fields, smoothed=smoothed)
            for field in fields:
                np.add(new_fields[field], cg[field][1: ,1: ,1: ], new_fields[field])
                np.add(new_fields[field], cg[field][:-1,1: ,1: ], new_fields[field])
                np.add(new_fields[field], cg[field][1: ,:-1,1: ], new_fields[field])
                np.add(new_fields[field], cg[field][1: ,1: ,:-1], new_fields[field])
                np.add(new_fields[field], cg[field][:-1,1: ,:-1], new_fields[field])
                np.add(new_fields[field], cg[field][1: ,:-1,:-1], new_fields[field])
                np.add(new_fields[field], cg[field][:-1,:-1,1: ], new_fields[field])
                np.add(new_fields[field], cg[field][:-1,:-1,:-1], new_fields[field])
                np.multiply(new_fields[field], 0.125, new_fields[field])

        if _old_api:
            return new_fields[fields[0]]
        return new_fields