    def forward(self, *args):
        """
        *args - The arguments representing the PSD matrix A (or batch of PSD matrices A)
        If self.inv_quad is true, the first entry in *args is inv_quad_rhs (Tensor)
        - the RHS of the matrix solves.

        Returns:
        - (Scalar) The inverse quadratic form (or None, if self.inv_quad is False)
        - (Scalar) The log determinant (or None, self.if logdet is False)
        """
        matrix_args = None
        inv_quad_rhs = None
        if self.inv_quad:
            matrix_args = args[1:]
            inv_quad_rhs = args[0]
        else:
            matrix_args = args

        # Get closure for matmul
        lazy_tsr = self.representation_tree(*matrix_args)

        # Collect terms for LinearCG
        # We use LinearCG for both matrix solves and for stochastically estimating the log det
        rhs_list = []
        num_random_probes = 0
        num_inv_quad_solves = 0

        # RHS for logdet
        if self.logdet:
            rhs_list.append(self.probe_vectors)
            num_random_probes = self.probe_vectors.size(-1)

        # RHS for inv_quad
        self.is_vector = False
        if self.inv_quad:
            if inv_quad_rhs.ndimension() == 1:
                inv_quad_rhs = inv_quad_rhs.unsqueeze(-1)
                self.is_vector = True
            rhs_list.append(inv_quad_rhs)
            num_inv_quad_solves = inv_quad_rhs.size(-1)

        # Perform solves (for inv_quad) and tridiagonalization (for estimating logdet)
        rhs = torch.cat(rhs_list, -1)
        t_mat = None
        if self.logdet and settings.skip_logdet_forward.off():
            solves, t_mat = lazy_tsr._solve(rhs, self.preconditioner, num_tridiag=num_random_probes)

        else:
            solves = lazy_tsr._solve(rhs, self.preconditioner, num_tridiag=0)

        # Final values to return
        logdet_term = torch.zeros(lazy_tsr.batch_shape, dtype=self.dtype, device=self.device)
        inv_quad_term = torch.zeros(lazy_tsr.batch_shape, dtype=self.dtype, device=self.device)

        # Compute logdet from tridiagonalization
        if self.logdet and settings.skip_logdet_forward.off():
            if torch.any(torch.isnan(t_mat)).item():
                logdet_term = torch.tensor(float("nan"), dtype=self.dtype, device=self.device)
            else:
                if self.batch_shape is None:
                    t_mat = t_mat.unsqueeze(1)
                eigenvalues, eigenvectors = lanczos_tridiag_to_diag(t_mat)
                slq = StochasticLQ()
                logdet_term, = slq.evaluate(self.matrix_shape, eigenvalues, eigenvectors, [lambda x: x.log()])

                # Add correction
                if self.logdet_correction is not None:
                    logdet_term = logdet_term + self.logdet_correction

        # Extract inv_quad solves from all the solves
        if self.inv_quad:
            inv_quad_solves = solves.narrow(-1, num_random_probes, num_inv_quad_solves)
            inv_quad_term = (inv_quad_solves * inv_quad_rhs).sum(-2)

        self.num_random_probes = num_random_probes
        self.num_inv_quad_solves = num_inv_quad_solves

        to_save = list(matrix_args) + [solves, ]
        self.save_for_backward(*to_save)

        if settings.memory_efficient.off():
            self._lazy_tsr = lazy_tsr

        return inv_quad_term, logdet_term