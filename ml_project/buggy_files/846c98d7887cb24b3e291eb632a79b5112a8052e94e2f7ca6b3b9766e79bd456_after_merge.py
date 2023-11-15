    def _fill_fields(self, fields):
        fields = [f for f in fields if f not in self.field_data]
        if len(fields) == 0:
            return
        ls = self._initialize_level_state(fields)
        min_level = self._compute_minimum_level()
        # NOTE: This usage of "refine_by" is actually *okay*, because it's
        # being used with respect to iref, which is *already* scaled!
        refine_by = self.ds.refine_by
        if not iterable(self.ds.refine_by):
            refine_by = [refine_by, refine_by, refine_by]
        refine_by = np.array(refine_by, dtype="i8")

        runtime_errors_count = 0
        for level in range(self.level + 1):
            if level < min_level:
                self._update_level_state(ls)
                continue
            nd = self.ds.dimensionality
            refinement = np.zeros_like(ls.base_dx)
            refinement += self.ds.relative_refinement(0, ls.current_level)
            refinement[nd:] = 1
            domain_dims = self.ds.domain_dimensions * refinement
            domain_dims = domain_dims.astype("int64")
            tot = ls.current_dims.prod()
            for chunk in ls.data_source.chunks(fields, "io"):
                chunk[fields[0]]
                input_fields = [chunk[field] for field in fields]
                tot -= fill_region(
                    input_fields,
                    ls.fields,
                    ls.current_level,
                    ls.global_startindex,
                    chunk.icoords,
                    chunk.ires,
                    domain_dims,
                    refine_by,
                )
            if level == 0 and tot != 0:
                runtime_errors_count += 1
            self._update_level_state(ls)
        if runtime_errors_count:
            warnings.warn(
                "Something went wrong during field computation. "
                "This is likely due to missing ghost-zones support "
                "in class %s",
                self.ds.__class__,
                category=RuntimeWarning,
            )
            mylog.debug(f"Caught {runtime_errors_count} runtime errors.")
        for name, v in zip(fields, ls.fields):
            if self.level > 0:
                v = v[1:-1, 1:-1, 1:-1]
            fi = self.ds._get_field_info(*name)
            self[name] = self.ds.arr(v, fi.units)