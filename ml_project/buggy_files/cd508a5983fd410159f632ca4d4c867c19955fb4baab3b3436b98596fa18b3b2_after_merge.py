    def trans(self):
        """Transposed operator.

        Returns
        -------
        oper : qobj
            Transpose of input operator.

        """
        out = Qobj()
        out.data = self.data.T.tocsr()
        out.dims = [self.dims[1], self.dims[0]]
        out.shape = [self.shape[1], self.shape[0]]
        return out