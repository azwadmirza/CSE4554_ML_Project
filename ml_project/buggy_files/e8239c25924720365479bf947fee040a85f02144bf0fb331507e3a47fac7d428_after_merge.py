    def _read_fluid_selection(self, chunks, selector, fields, size):
        """Reads given fields masked by a given selection.

        Parameters
        ----------
        chunks
            A list of chunks
            A chunk is a list of grids
        selector
            A region (inside your domain) specifying which parts of the field you want to read
            See [1] and [2]
        fields : array_like
            Tuples (fname, ftype) representing a field
        size : int
            Size of the data to read

        Returns
        -------
        dict
            keys are tuples (ftype, fname) representing a field
            values are flat (``size``,) ndarrays with data from that field
        """
        f = self._handle
        bp = self.base_path
        mp = self.meshes_path
        ds = f[bp + mp]
        chunks = list(chunks)

        rv = {}
        ind = {}

        if isinstance(selector, GridSelector):
            if not (len(chunks) == len(chunks[0].objs) == 1):
                raise RuntimeError

        if size is None:
            size = sum((g.count(selector) for chunk in chunks
                        for g in chunk.objs))
        for field in fields:
            rv[field] = np.empty(size, dtype=np.float64)
            ind[field] = 0

        for (ftype, fname) in fields:
            field = (ftype, fname)
            for chunk in chunks:
                for grid in chunk.objs:
                    mask = grid._get_selector_mask(selector)
                    if mask is None:
                        continue
                    component = fname.replace("_", "/").replace("-", "_")
                    if component.split("/")[0] not in grid.ftypes:
                        data = np.full(grid.ActiveDimensions, 0, dtype=np.float64)
                    else:
                        data = get_component(ds, component, grid.findex, grid.foffset)
                    # The following is a modified AMRGridPatch.select(...)
                    data.shape = mask.shape  # Workaround - casts a 2D (x,y) array to 3D (x,y,1)
                    count = grid.count(selector)
                    rv[field][ind[field]:ind[field] + count] = data[mask]
                    ind[field] += count

        for field in fields:
            rv[field] = rv[field][:ind[field]]
            rv[field].flatten()

        return rv