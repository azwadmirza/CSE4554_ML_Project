    def read_direct(self, dest, source_sel=None, dest_sel=None):
        """ Read data directly from HDF5 into an existing NumPy array.

        The destination array must be C-contiguous and writable.
        Selections must be the output of numpy.s_[<args>].

        Broadcasting is supported for simple indexing.
        """
        with phil:
            if self._is_empty:
                raise TypeError("Empty datasets have no numpy representation")
            if source_sel is None:
                source_sel = sel.SimpleSelection(self.shape)
            else:
                source_sel = sel.select(self.shape, source_sel, self)  # for numpy.s_
            fspace = source_sel.id

            if dest_sel is None:
                dest_sel = sel.SimpleSelection(dest.shape)
            else:
                dest_sel = sel.select(dest.shape, dest_sel)

            for mspace in dest_sel.broadcast(source_sel.mshape):
                self.id.read(mspace, fspace, dest, dxpl=self._dxpl)