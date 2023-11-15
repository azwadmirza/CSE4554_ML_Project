    def __init__(self, lower_bound, upper_bound, transform=sigmoid, inv_transform=inv_sigmoid, initial_value=None):
        """
        Defines an interval constraint for GP model parameters, specified by a lower bound and upper bound. For usage
        details, see the documentation for :meth:`~gpytorch.module.Module.register_constraint`.

        Args:
            lower_bound (float or torch.Tensor): The lower bound on the parameter.
            upper_bound (float or torch.Tensor): The upper bound on the parameter.
        """
        lower_bound = torch.as_tensor(lower_bound).float()
        upper_bound = torch.as_tensor(upper_bound).float()

        if torch.any(torch.ge(lower_bound, upper_bound)):
            raise RuntimeError("Got parameter bounds with empty intervals.")

        super().__init__()

        self.register_buffer("lower_bound", lower_bound)
        self.register_buffer("upper_bound", upper_bound)

        self._transform = transform
        self._inv_transform = inv_transform
        self._initial_value = initial_value

        if transform is not None and inv_transform is None:
            self._inv_transform = _get_inv_param_transform(transform)