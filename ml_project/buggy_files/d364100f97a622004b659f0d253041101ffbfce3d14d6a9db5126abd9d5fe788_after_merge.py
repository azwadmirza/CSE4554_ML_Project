    def write_direct(self, source, source_sel=None, dest_sel=None):
        """ Write data directly to HDF5 from a NumPy array.

        The source array must be C-contiguous.  Selections must be
        the output of numpy.s_[<args>].

        Broadcasting is supported for simple indexing.
        """
        with phil:
            if self._is_empty:
                raise TypeError("Empty datasets cannot be written to")
            if source_sel is None:
                source_sel = sel.SimpleSelection(source.shape)
            else:
                source_sel = sel.select(source.shape, source_sel)  # for numpy.s_
            mspace = source_sel.id

            if dest_sel is None:
                dest_sel = sel.SimpleSelection(self.shape)
            else:
                dest_sel = sel.select(self.shape, dest_sel, self)

            for fspace in dest_sel.broadcast(source_sel.mshape):
                self.id.write(mspace, fspace, source, dxpl=self._dxpl)