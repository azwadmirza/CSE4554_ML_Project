    def field_arrays(self):
        """ Returns all field arrays """
        fdata = self.GetFieldData()
        narr = fdata.GetNumberOfArrays()

        # just return if unmodified
        if hasattr(self, '_field_arrays'):
            keys = list(self._field_arrays.keys())
            if narr == len(keys):
                return self._field_arrays

        # dictionary with callbacks
        self._field_arrays = FieldScalarsDict(self)

        for i in range(narr):
            name = fdata.GetArrayName(i)
            if name is None or len(name) < 1:
                name = 'Field Array {}'.format(i)
                fdata.GetArray(i).SetName(name)
            self._field_arrays[name] = self._field_scalar(name)

        self._field_arrays.enable_callback()
        return self._field_arrays