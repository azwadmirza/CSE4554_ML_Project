    def conj(self):
        """Conjugate operator of quantum object.

        """
        out = Qobj()
        out.data = self.data.conj()
        out.dims = [self.dims[1], self.dims[0]]
        out.shape = [self.shape[1], self.shape[0]]
        return out