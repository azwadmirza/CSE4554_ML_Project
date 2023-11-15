    def forward(self, *args):
        left_tensor = None
        right_tensor = None
        matrix_args = None
        if self.has_left:
            left_tensor, right_tensor, *matrix_args = args
        else:
            right_tensor, *matrix_args = args
        orig_right_tensor = right_tensor
        lazy_tsr = self.representation_tree(*matrix_args)

        with torch.no_grad():
            self.preconditioner = lazy_tsr.detach()._inv_matmul_preconditioner()

        self.is_vector = False
        if right_tensor.ndimension() == 1:
            right_tensor = right_tensor.unsqueeze(-1)
            self.is_vector = True

        # Perform solves (for inv_quad) and tridiagonalization (for estimating logdet)
        if self.has_left:
            rhs = torch.cat([left_tensor.transpose(-1, -2), right_tensor], -1)
            solves = lazy_tsr._solve(rhs, self.preconditioner)
            res = solves[..., left_tensor.size(-2):]
            res = left_tensor @ res
        else:
            solves = lazy_tsr._solve(right_tensor, self.preconditioner)
            res = solves

        if self.is_vector:
            res = res.squeeze(-1)

        if self.has_left:
            args = [solves, left_tensor, orig_right_tensor] + list(matrix_args)
        else:
            args = [solves, orig_right_tensor] + list(matrix_args)
        self.save_for_backward(*args)
        if settings.memory_efficient.off():
            self._lazy_tsr = lazy_tsr

        return res