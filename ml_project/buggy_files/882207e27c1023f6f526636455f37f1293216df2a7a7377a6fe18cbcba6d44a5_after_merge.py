    def unique(self):
        """
        Return array of unique values in the Series. Significantly faster than
        numpy.unique

        Returns
        -------
        uniques : ndarray
        """
        values = self.values
        if issubclass(values.dtype.type, np.floating):
            table = lib.Float64HashTable(len(values))
            uniques = np.array(table.unique(values), dtype='f8')
        else:
            if not values.dtype == np.object_:
                values = values.astype('O')
            table = lib.PyObjectHashTable(len(values))
            uniques = lib.list_to_object_array(table.unique(values))
            uniques = lib.maybe_convert_objects(uniques)
        return uniques