    def norm(self, norm=None, sparse=False, tol=0, maxiter=100000):
        """Norm of a quantum object.

        Default norm is L2-norm for kets and trace-norm for operators.
        Other ket and operator norms may be specified using the 
        `ket_norm` and `oper_norm` arguments.

        Parameters
        ----------
        norm : str
            Which norm to use for ket/bra vectors: L2 'l2', max norm 'max',
            or for operators: trace 'tr', Frobius 'fro', one 'one', or max 'max'.
        
        sparse : bool
            Use sparse eigenvalue solver for trace norm.  Other norms are not
            affected by this parameter.

        tol : float
            Tolerance for sparse solver (if used) for trace norm. The sparse
            solver may not converge if the tolerance is set too low.

        maxiter : int
            Maximum number of iterations performed by sparse solver (if used)
            for trace norm.

        Returns
        -------
        norm : float
            The requested norm of the operator or state quantum object.


        Notes
        -----
        The sparse eigensolver is much slower than the dense version.
        Use sparse only if memory requirements demand it.

        """
        if self.type == 'oper' or self.type == 'super':
            if norm is None or norm == 'tr':
                vals = sp_eigs(self, vecs=False, sparse=sparse,
                               tol=tol, maxiter=maxiter)
                return np.sum(sqrt(abs(vals) ** 2))
            elif norm == 'fro':
                return _sp_fro_norm(self)
            elif norm == 'one':
                return _sp_one_norm(self)
            elif norm == 'max':
                return _sp_max_norm(self)
            else:
                raise ValueError(
                    "Operator norm must be 'tr', 'fro', 'one', or 'max'.")
        else:
            if norm==None:
                norm = 'l2'
            if norm == 'l2':
                return _sp_L2_norm(self)
            elif norm == 'max':
                return _sp_max_norm(self)
            else:
                raise ValueError(
                    "Ket norm must be 'l2', or 'max'.")