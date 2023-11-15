    def backward(ctx, inv_quad_grad_output, logdet_grad_output):
        matrix_arg_grads = None
        inv_quad_rhs_grad = None

        # Which backward passes should we compute?
        compute_inv_quad_grad = inv_quad_grad_output.abs().sum() and ctx.inv_quad
        compute_logdet_grad = logdet_grad_output.abs().sum() and ctx.logdet

        # Get input arguments, and get gradients in the proper form
        matrix_args = ctx.saved_tensors[:-1]
        solves = ctx.saved_tensors[-1]

        if hasattr(ctx, "_lazy_tsr"):
            lazy_tsr = ctx._lazy_tsr
        else:
            lazy_tsr = ctx.representation_tree(*matrix_args)

        # Fix grad_output sizes
        if ctx.inv_quad:
            inv_quad_grad_output = inv_quad_grad_output.unsqueeze(-2)
        if compute_logdet_grad:
            logdet_grad_output = logdet_grad_output.unsqueeze(-1)
            logdet_grad_output.unsqueeze_(-1)

        # Divide up the solves
        probe_vector_solves = None
        inv_quad_solves = None
        neg_inv_quad_solves_times_grad_out = None
        if compute_logdet_grad:
            coef = 1.0 / ctx.probe_vectors.size(-1)
            probe_vector_solves = solves.narrow(-1, 0, ctx.num_random_probes).mul(coef)
            probe_vector_solves.mul_(ctx.probe_vector_norms).mul_(logdet_grad_output)
            probe_vectors = ctx.probe_vectors.mul(ctx.probe_vector_norms)
        if ctx.inv_quad:
            inv_quad_solves = solves.narrow(-1, ctx.num_random_probes, ctx.num_inv_quad_solves)
            neg_inv_quad_solves_times_grad_out = inv_quad_solves.mul(inv_quad_grad_output).mul_(-1)

        # input_1 gradient
        if any(ctx.needs_input_grad):
            # Collect terms for arg grads
            left_factors_list = []
            right_factors_list = []

            if compute_logdet_grad:
                left_factors_list.append(probe_vector_solves)
                if ctx.preconditioner is not None:
                    probe_vectors = ctx.preconditioner(probe_vectors)
                right_factors_list.append(probe_vectors)

            if compute_inv_quad_grad:
                left_factors_list.append(neg_inv_quad_solves_times_grad_out)
                right_factors_list.append(inv_quad_solves)

            left_factors = torch.cat(left_factors_list, -1)
            right_factors = torch.cat(right_factors_list, -1)
            matrix_arg_grads = lazy_tsr._quad_form_derivative(left_factors, right_factors)

        # input_2 gradients
        if compute_inv_quad_grad and ctx.needs_input_grad[9]:
            inv_quad_rhs_grad = neg_inv_quad_solves_times_grad_out.mul_(-2)
        elif ctx.inv_quad:
            inv_quad_rhs_grad = torch.zeros_like(inv_quad_solves)
        if ctx.is_vector:
            inv_quad_rhs_grad.squeeze_(-1)

        if ctx.inv_quad:
            res = [inv_quad_rhs_grad] + list(matrix_arg_grads)
        else:
            res = matrix_arg_grads

        return tuple([None] * 9 + res)