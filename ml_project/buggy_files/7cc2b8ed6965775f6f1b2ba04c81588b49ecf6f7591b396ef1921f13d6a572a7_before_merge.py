    def __init__(
        self,
        num_tasks,
        rank=0,
        task_correlation_prior=None,
        batch_size=1,
        noise_prior=None,
        param_transform=softplus,
        inv_param_transform=None,
        **kwargs
    ):
        """
        Args:
            num_tasks (int): Number of tasks.

            rank (int): The rank of the task noise covariance matrix to fit. If `rank` is set to 0,
            then a diagonal covariance matrix is fit.

            task_correlation_prior (:obj:`gpytorch.priors.Prior`): Prior to use over the task noise correlaton matrix.
            Only used when `rank` > 0.

        """
        task_correlation_prior = _deprecate_kwarg(
            kwargs, "task_prior", "task_correlation_prior", task_correlation_prior
        )
        noise_covar = MultitaskHomoskedasticNoise(
            num_tasks=num_tasks,
            noise_prior=noise_prior,
            batch_size=batch_size,
            param_transform=param_transform,
            inv_param_transform=inv_param_transform,
        )
        super().__init__(
            num_tasks=num_tasks,
            noise_covar=noise_covar,
            rank=rank,
            task_correlation_prior=task_correlation_prior,
            batch_size=batch_size,
        )
        self._param_transform = param_transform
        self._inv_param_transform = _get_inv_param_transform(param_transform, inv_param_transform)
        self.register_parameter(name="raw_noise", parameter=torch.nn.Parameter(torch.zeros(batch_size, 1)))