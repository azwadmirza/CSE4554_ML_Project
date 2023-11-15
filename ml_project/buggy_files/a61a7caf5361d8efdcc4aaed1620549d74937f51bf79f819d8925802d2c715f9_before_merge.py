    def __mul__(self, other):
        """
        MULTIPLICATION with Qobj on LEFT [ ex. Qobj*4 ]
        """
        if isinstance(other, Qobj):
            if (self.shape[1] == other.shape[0] and
                    self.dims[1] == other.dims[0]):
                out = Qobj()
                out.data = self.data * other.data
                dims = [self.dims[0], other.dims[1]]
                out.dims = dims
                if not isinstance(dims[0][0], list):
                    r = range(len(dims[0]))
                    mask = [dims[0][n] == dims[1][n] == 1 for n in r]
                    out.dims = [max([1], [dims[0][n] for n in r if not mask[n]]),
                                max([1], [dims[1][n] for n in r if not mask[n]])]
                else:
                    out.dims = dims
                out.shape = [self.shape[0], other.shape[1]]
                out.type = _typecheck(out)
                out._isherm = out.isherm
                return out.tidyup() if qset.auto_tidyup else out

            elif (self.shape[0] == 1 and self.shape[1] == 1):
                out = Qobj(other)
                out.data *= self.data[0,0]
                return out.tidyup() if qset.auto_tidyup else out

            elif (other.shape[0] == 1 and other.shape[1] == 1):
                out = Qobj(self)
                out.data *= other.data[0,0]
                return out.tidyup() if qset.auto_tidyup else out

            else:
                raise TypeError("Incompatible Qobj shapes")

        elif isinstance(other, (list, np.ndarray)):
            # if other is a list, do element-wise multiplication
            return np.array([self * item for item in other])

        elif _checkeseries(other) == 'eseries':
            return other.__rmul__(self)

        elif isinstance(other, (int, float, complex, np.int64)):
            out = Qobj(type=self.type)
            out.data = self.data * other
            out.dims = self.dims
            out.shape = self.shape
            if isinstance(other, complex):
                out._isherm = out.isherm
            else:
                out._isherm = self._isherm

            return out.tidyup() if qset.auto_tidyup else out

        else:
            raise TypeError("Incompatible object for multiplication")