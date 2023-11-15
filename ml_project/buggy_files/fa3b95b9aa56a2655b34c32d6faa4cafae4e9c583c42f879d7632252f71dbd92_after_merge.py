    def dag(self):
        """Adjoint operator of quantum object.
        """
        out = Qobj()
        out.data = self.data.T.conj().tocsr()
        out.dims = [self.dims[1], self.dims[0]]
        out.shape = [self.shape[1], self.shape[0]]
        out._isherm = self._isherm
        return out