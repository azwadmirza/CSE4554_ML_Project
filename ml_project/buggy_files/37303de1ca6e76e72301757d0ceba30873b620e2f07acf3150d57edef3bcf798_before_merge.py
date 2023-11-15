    def __div__(self, other):
        """
        DIVISION (by numbers only)
        """
        if isinstance(other, Qobj):  # if both are quantum objects
            raise TypeError("Incompatible Qobj shapes " +
                            "[division with Qobj not implemented]")

        if isinstance(other, (int, float, complex, np.int64)):
            out = Qobj(type=self.type)
            out.data = self.data / other
            out.dims = self.dims
            out.shape = self.shape
            if isinstance(other, (int, float, np.int64)):
                out._isherm = self._isherm
            else:
                out._isherm = out.isherm

            return out.tidyup() if qset.auto_tidyup else out

        else:
            raise TypeError("Incompatible object for division")