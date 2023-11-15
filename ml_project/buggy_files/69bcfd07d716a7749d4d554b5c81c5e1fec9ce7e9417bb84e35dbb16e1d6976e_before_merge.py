    def ravel(self, order='C'):
        if order not in 'CFA':
            raise ValueError('order not C|F|A')

        if self.ndim <= 1:
            return self

        elif (order == 'C' and self.is_c_contig or
                          order == 'F' and self.is_f_contig):
            newshape = (self.size,)
            newstrides = (self.itemsize,)
            arr = self.from_desc(self.extent.begin, newshape, newstrides,
                                 self.itemsize)
            return arr, list(self.iter_contiguous_extent())

        else:
            raise NotImplementedError("ravel on non-contiguous array")