    def _fill_fields(self, fields):
        fields = [f for f in fields if f not in self.field_data]
        if len(fields) == 0: return
        # It may be faster to adapt fill_region_float to fill multiple fields
        # instead of looping here
        for field in fields:
            dest = np.zeros(self.ActiveDimensions, dtype="float64")
            for chunk in self._data_source.chunks(fields, "io"):
                fill_region_float(chunk.fcoords, chunk.fwidth, chunk[field],
                                  self.left_edge, self.right_edge, dest, 1,
                                  self.ds.domain_width,
                                  int(any(self.ds.periodicity)))
            fi = self.ds._get_field_info(field)
            self[field] = self.ds.arr(dest, fi.units)