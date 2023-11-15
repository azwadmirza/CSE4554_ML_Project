    def __rmul__(self, other):
        """
        MULTIPLICATION with Qobj on RIGHT [ ex. 4*Qobj ]
        """
        if isinstance(other, Qobj):  # if both are quantum objects
            if (self.shape[1] == other.shape[0] and
                    self.dims[1] == other.dims[0]):
                out = Qobj()
                out.data = other.data * self.data
                out.dims = self.dims
                out.shape = [self.shape[0], other.shape[1]]
                out.type = _typecheck(out)
                out._isherm = out.isherm
                return out.tidyup() if qset.auto_tidyup else out

            else:
                raise TypeError("Incompatible Qobj shapes")

        if isinstance(other, (list, np.ndarray)):
            # if other is a list, do element-wise multiplication
            return np.array([item * self for item in other])

        if _checkeseries(other) == 'eseries':
            return other.__mul__(self)

        if isinstance(other, (int, float, complex, np.int64)):
            out = Qobj(type=self.type)
            out.data = other * self.data
            out.dims = self.dims
            out.shape = self.shape
            if isinstance(other, (int, float, np.int64)):
                out._isherm = self._isherm
            else:
                out._isherm = out.isherm

            return out.tidyup() if qset.auto_tidyup else out

        else:
            raise TypeError("Incompatible object for multiplication")