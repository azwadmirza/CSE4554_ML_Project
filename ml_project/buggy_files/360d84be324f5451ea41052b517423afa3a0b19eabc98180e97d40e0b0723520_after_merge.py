    def cell_arrays(self):
        """ Returns the all cell arrays """
        cdata = self.GetCellData()
        narr = cdata.GetNumberOfArrays()

        # Update data if necessary
        if hasattr(self, '_cell_arrays'):
            keys = list(self._cell_arrays.keys())
            if narr == len(keys):
                if keys:
                    if self._cell_arrays[keys[0]].shape[0] == self.n_cells:
                        return self._cell_arrays
                else:
                    return self._cell_arrays

        # dictionary with callbacks
        self._cell_arrays = CellScalarsDict(self)

        for i in range(narr):
            name = cdata.GetArrayName(i)
            if name is None or len(name) < 1:
                name = 'Cell Array {}'.format(i)
                cdata.GetArray(i).SetName(name)
            self._cell_arrays[name] = self._cell_scalar(name)

        self._cell_arrays.enable_callback()
        return self._cell_arrays