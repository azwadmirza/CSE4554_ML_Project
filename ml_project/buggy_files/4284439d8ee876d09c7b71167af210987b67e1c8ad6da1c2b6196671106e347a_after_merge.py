    def from_independent_mvns(cls, mvns):
        """
        Convert an iterable of MVNs into a :obj:`~gpytorch.distributions.MultitaskMultivariateNormal`.
        The resulting distribution will have :attr:`len(mvns)` tasks, and the tasks will be independent.

        :param ~gpytorch.distributions.MultitaskNormal mvn: The base MVN distributions.
        :returns: the independent multitask distribution
        :rtype: gpytorch.distributions.MultitaskMultivariateNormal

        Example:
            >>> # model is a gpytorch.models.VariationalGP
            >>> # likelihood is a gpytorch.likelihoods.Likelihood
            >>> mean = torch.randn(4, 3)
            >>> covar_factor = torch.randn(4, 3, 3)
            >>> covar = covar_factor @ covar_factor.transpose(-1, -2)
            >>> mvn1 = gpytorch.distributions.MultivariateNormal(mean, covar)
            >>>
            >>> mean = torch.randn(4, 3)
            >>> covar_factor = torch.randn(4, 3, 3)
            >>> covar = covar_factor @ covar_factor.transpose(-1, -2)
            >>> mvn2 = gpytorch.distributions.MultivariateNormal(mean, covar)
            >>>
            >>> mmvn = MultitaskMultivariateNormal.from_independent_mvns([mvn1, mvn2])
            >>> print(mmvn.event_shape, mmvn.batch_shape)
            >>> # torch.Size([3, 2]), torch.Size([4])
        """
        if len(mvns) < 2:
            raise ValueError("Must provide at least 2 MVNs to form a MultitaskMultivariateNormal")
        if any(isinstance(mvn, MultitaskMultivariateNormal) for mvn in mvns):
            raise ValueError("Cannot accept MultitaskMultivariateNormals")
        if not all(m.batch_shape == mvns[0].batch_shape for m in mvns[1:]):
            raise ValueError("All MultivariateNormals must have the same batch shape")
        if not all(m.event_shape == mvns[0].event_shape for m in mvns[1:]):
            raise ValueError("All MultivariateNormals must have the same event shape")
        mean = torch.stack([mvn.mean for mvn in mvns], -1)
        # TODO: To do the following efficiently, we don't want to evaluate the
        # covariance matrices. Instead, we want to use the lazies directly in the
        # BlockDiagLazyTensor. This will require implementing a new BatchLazyTensor:

        # https://github.com/cornellius-gp/gpytorch/issues/468
        covar_blocks_lazy = CatLazyTensor(
            *[mvn.lazy_covariance_matrix.unsqueeze(0) for mvn in mvns],
            dim=0,
            output_device=mean.device
        )
        covar_lazy = BlockDiagLazyTensor(covar_blocks_lazy, block_dim=0)
        return cls(mean=mean, covariance_matrix=covar_lazy, interleaved=False)