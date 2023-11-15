    def transform(self, inpt, inverse=False):
        """Basis transform defined by input array.

        Input array can be a ``matrix`` defining the transformation,
        or a ``list`` of kets that defines the new basis.


        Parameters
        ----------
        inpt : array_like
            A ``matrix`` or ``list`` of kets defining the transformation.
        inverse : bool
            Whether to return inverse transformation.


        Returns
        -------
        oper : qobj
            Operator in new basis.


        Notes
        -----
        This function is still in development.


        """
        if isinstance(inpt, list) or isinstance(inpt, np.ndarray):
            if len(inpt) != max(self.shape):
                raise TypeError(
                    'Invalid size of ket list for basis transformation')
            S = np.matrix(np.hstack([psi.full() for psi in inpt])).H
        elif isinstance(inpt, np.ndarray):
            S = np.matrix(inpt)
        else:
            raise TypeError('Invalid operand for basis transformation')

        # normalize S just in case the supplied basis states aren't normalized
        # S = S/la.norm(S)

        out = Qobj(dims=self.dims, shape=self.shape)
        out._isherm = self._isherm
        out.superrep = self.superrep

        # transform data
        if inverse:
            if isket(self):
                out.data = S.H * self.data
            elif isbra(self):
                out.data = self.data * S
            else:
                out.data = S.H * self.data * S
        else:
            if isket(self):
                out.data = S * self.data
            elif isbra(self):
                out.data = self.data * S.H
            else:
                out.data = S * self.data * S.H

        # force sparse
        out.data = sp.csr_matrix(out.data, dtype=complex)

        return out