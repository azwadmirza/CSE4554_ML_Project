    def __add__(self, other):  # defines left addition for Qobj class
        """
        ADDITION with Qobj on LEFT [ ex. Qobj+4 ]
        """
        if _checkeseries(other) == 'eseries':
            return other.__radd__(self)

        if not isinstance(other, Qobj):
            other = Qobj(other)

        if np.prod(other.shape) == 1 and np.prod(self.shape) != 1:
            # case for scalar quantum object
            dat = np.array(other.full())[0][0]
            if dat == 0:
                return self

            out = Qobj()

            if self.type in ['oper', 'super']:
                out.data = self.data + dat * sp.identity(
                    self.shape[0], dtype=complex, format='csr')
            else:
                out.data = self.data
                out.data.data = out.data.data + dat

            out.dims = self.dims
            out.shape = self.shape
            if isinstance(dat, (int, float)):
                out._isherm = self._isherm
            else:
                out._isherm = out.isherm
   
            return out.tidyup() if qset.auto_tidyup else out


        elif np.prod(self.shape) == 1 and np.prod(other.shape) != 1:
            # case for scalar quantum object
            dat = np.array(self.full())[0][0]
            if dat == 0:
                return other

            out = Qobj()
            if other.type in ['oper', 'super']:
                out.data = dat * sp.identity(other.shape[0], dtype=complex,
                                             format='csr') + other.data
            else:
                out.data = other.data
                out.data.data = out.data.data + dat
            out.dims = other.dims
            out.shape = other.shape

            if isinstance(dat, (int, float)):
                out._isherm = self._isherm
            else:
                out._isherm = out.isherm
   
            return out.tidyup() if qset.auto_tidyup else out

        elif self.dims != other.dims:
            raise TypeError('Incompatible quantum object dimensions')

        elif self.shape != other.shape:
            raise TypeError('Matrix shapes do not match')

        else:  # case for matching quantum objects
            out = Qobj()
            out.data = self.data + other.data
            out.dims = self.dims
            out.shape = self.shape

            if self.type in ['ket', 'bra', 'super']:
                out._isherm = False
            elif self._isherm and self._isherm == other._isherm:
                out._isherm = True
            elif self._isherm and not other._isherm:
                out._isherm = False
            elif not self._isherm and other._isherm:
                out._isherm = False
            else:
                out._isherm = out.isherm

            return out.tidyup() if qset.auto_tidyup else out