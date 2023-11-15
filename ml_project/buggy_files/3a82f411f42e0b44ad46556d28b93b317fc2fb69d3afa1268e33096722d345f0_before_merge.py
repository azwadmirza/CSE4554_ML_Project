    def read(self, nrows=None):

        if (nrows is None) and (self.chunksize is not None):
            nrows = self.chunksize
        elif nrows is None:
            nrows = self.row_count

        if self._current_row_in_file_index >= self.row_count:
            return None

        nd = (self.column_types == b'd').sum()
        ns = (self.column_types == b's').sum()

        self._string_chunk = np.empty((ns, nrows), dtype=np.object)
        self._byte_chunk = np.empty((nd, 8 * nrows), dtype=np.uint8)

        self._current_row_in_chunk_index = 0
        p = Parser(self)
        p.read(nrows)

        rslt = self._chunk_to_dataframe()
        if self.index is not None:
            rslt = rslt.set_index(self.index)

        return rslt