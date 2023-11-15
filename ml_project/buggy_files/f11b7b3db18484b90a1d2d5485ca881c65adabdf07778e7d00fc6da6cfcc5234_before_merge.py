    def __neg__(self):
        """
        NEGATION operation.
        """
        out = Qobj()
        out.data = -self.data
        out.dims = self.dims
        out.shape = self.shape
        out.type = self.type
        out._isherm = self._isherm
        return out.tidyup() if qset.auto_tidyup else out