    def forward(self, x):
        """
        The :func:`~gpytorch.variational.VariationalStrategy.forward` method determines how to marginalize out the
        inducing point function values. Specifically, forward defines how to transform a variational distribution
        over the inducing point values, :math:`q(u)`, in to a variational distribution over the function values at
        specified locations x, :math:`q(f|x)`, by integrating :math:`\int p(f|x, u)q(u)du`

        Args:
            x (torch.tensor): Locations x to get the variational posterior of the function values at.
        Returns:
            :obj:`gpytorch.distributions.MultivariateNormal`: The distribution q(f|x)
        """
        variational_dist = self.variational_distribution.variational_distribution
        inducing_points = self.inducing_points
        inducing_batch_shape = inducing_points.shape[:-2]
        if inducing_batch_shape < x.shape[:-2]:
            batch_shape = _mul_broadcast_shape(inducing_points.shape[:-2], x.shape[:-2])
            inducing_points = inducing_points.expand(*batch_shape, *inducing_points.shape[-2:])
            x = x.expand(*batch_shape, *x.shape[-2:])
            variational_dist = variational_dist.expand(batch_shape)

        # If our points equal the inducing points, we're done
        if torch.equal(x, inducing_points):
            return variational_dist

        # Otherwise, we have to marginalize
        else:
            num_induc = inducing_points.size(-2)
            full_inputs = torch.cat([inducing_points, x], dim=-2)
            full_output = self.model.forward(full_inputs)
            full_mean, full_covar = full_output.mean, full_output.lazy_covariance_matrix

            # Mean terms
            test_mean = full_mean[..., num_induc:]
            induc_mean = full_mean[..., :num_induc]
            mean_diff = (variational_dist.mean - induc_mean).unsqueeze(-1)

            # Covariance terms
            induc_induc_covar = full_covar[..., :num_induc, :num_induc].add_jitter()
            induc_data_covar = full_covar[..., :num_induc, num_induc:].evaluate()
            data_data_covar = full_covar[..., num_induc:, num_induc:]
            root_variational_covar = variational_dist.lazy_covariance_matrix.root_decomposition().root.evaluate()

            # If we had to expand the inducing points, shrink the inducing mean and induc_induc_covar dimension
            # This makes everything more computationally efficient
            if len(inducing_batch_shape) < len(induc_induc_covar.batch_shape):
                index = tuple(0 for _ in range(len(induc_induc_covar.batch_shape) - len(inducing_batch_shape)))
                repeat_size = torch.Size((
                    tuple(induc_induc_covar.batch_shape[:len(index)])
                    + tuple(1 for _ in induc_induc_covar.batch_shape[len(index):])
                ))
                induc_induc_covar = BatchRepeatLazyTensor(induc_induc_covar.__getitem__(index), repeat_size)

            # If we're less than a certain size, we'll compute the Cholesky decomposition of induc_induc_covar
            cholesky = False
            if settings.fast_computations.log_prob.off() or (num_induc <= settings.max_cholesky_size.value()):
                induc_induc_covar = CholLazyTensor(induc_induc_covar.cholesky())
                cholesky = True

            # If we are making predictions and don't need variances, we can do things very quickly.
            if not self.training and settings.skip_posterior_variances.on():
                if not hasattr(self, "_mean_cache"):
                    self._mean_cache = induc_induc_covar.inv_matmul(mean_diff).detach()

                predictive_mean = torch.add(
                    test_mean,
                    induc_data_covar.transpose(-2, -1).matmul(self._mean_cache).squeeze(-1)
                )

                predictive_covar = ZeroLazyTensor(test_mean.size(-1), test_mean.size(-1))

                return MultivariateNormal(predictive_mean, predictive_covar)

            # Cache the CG results
            # For now: run variational inference without a preconditioner
            # The preconditioner screws things up for some reason
            with settings.max_preconditioner_size(0):
                # Cache the CG results
                left_tensors = torch.cat([mean_diff, root_variational_covar], -1)
                with torch.no_grad():
                    eager_rhs = torch.cat([left_tensors, induc_data_covar], -1)
                    solve, probe_vecs, probe_vec_norms, probe_vec_solves, tmats = CachedCGLazyTensor.precompute_terms(
                        induc_induc_covar, eager_rhs.detach(), logdet_terms=(not cholesky),
                        include_tmats=(not settings.skip_logdet_forward.on() and not cholesky)
                    )
                    eager_rhss = [
                        eager_rhs.detach(), eager_rhs[..., left_tensors.size(-1):].detach(),
                        eager_rhs[..., :left_tensors.size(-1)].detach()
                    ]
                    solves = [
                        solve.detach(), solve[..., left_tensors.size(-1):].detach(),
                        solve[..., :left_tensors.size(-1)].detach()
                    ]
                    if settings.skip_logdet_forward.on():
                        eager_rhss.append(torch.cat([probe_vecs, left_tensors], -1))
                        solves.append(torch.cat([probe_vec_solves, solve[..., :left_tensors.size(-1)]], -1))
                induc_induc_covar = CachedCGLazyTensor(
                    induc_induc_covar, eager_rhss=eager_rhss, solves=solves, probe_vectors=probe_vecs,
                    probe_vector_norms=probe_vec_norms, probe_vector_solves=probe_vec_solves,
                    probe_vector_tmats=tmats,
                )

            if self.training:
                self._memoize_cache["prior_distribution_memo"] = MultivariateNormal(induc_mean, induc_induc_covar)

            # Compute predictive mean/covariance
            inv_products = induc_induc_covar.inv_matmul(induc_data_covar, left_tensors.transpose(-1, -2))
            predictive_mean = torch.add(test_mean, inv_products[..., 0, :])
            predictive_covar = RootLazyTensor(inv_products[..., 1:, :].transpose(-1, -2))
            if self.training:
                interp_data_data_var, _ = induc_induc_covar.inv_quad_logdet(
                    induc_data_covar, logdet=False, reduce_inv_quad=False
                )
                data_covariance = DiagLazyTensor((data_data_covar.diag() - interp_data_data_var).clamp(0, math.inf))
            else:
                neg_induc_data_data_covar = torch.matmul(
                    induc_data_covar.transpose(-1, -2).mul(-1),
                    induc_induc_covar.inv_matmul(induc_data_covar)
                )
                data_covariance = data_data_covar + neg_induc_data_data_covar
            predictive_covar = PsdSumLazyTensor(predictive_covar, data_covariance)

            return MultivariateNormal(predictive_mean, predictive_covar)