    def unique(self):
        """
        Return array of unique values in the Series. Significantly faster than
        numpy.unique

        Returns
        -------
        uniques : ndarray
        """
        values = self.values
        if not values.dtype == np.object_:
            values = values.astype('O')
        table = lib.PyObjectHashTable(len(values))
        uniques = lib.list_to_object_array(table.unique(values))
        return lib.maybe_convert_objects(uniques)