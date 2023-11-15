    def __init__(
        self,
        base_lazy_tensor,
        left_interp_indices=None,
        left_interp_values=None,
        right_interp_indices=None,
        right_interp_values=None,
    ):
        base_lazy_tensor = lazify(base_lazy_tensor)

        if left_interp_indices is None:
            num_rows = base_lazy_tensor.size(-2)
            left_interp_indices = torch.arange(0, num_rows, dtype=torch.long, device=base_lazy_tensor.device)
            left_interp_indices.unsqueeze_(-1)
            left_interp_indices = left_interp_indices.expand(*base_lazy_tensor.batch_shape, num_rows, 1)

        if left_interp_values is None:
            left_interp_values = torch.ones(
                left_interp_indices.size(), dtype=base_lazy_tensor.dtype, device=base_lazy_tensor.device
            )

        if right_interp_indices is None:
            num_rows = base_lazy_tensor.size(-2)
            right_interp_indices = torch.arange(0, num_rows, dtype=torch.long, device=base_lazy_tensor.device)
            right_interp_indices.unsqueeze_(-1)
            right_interp_indices = right_interp_indices.expand(*base_lazy_tensor.batch_shape, num_rows, 1)

        if right_interp_values is None:
            right_interp_values = torch.ones(
                right_interp_indices.size(), dtype=base_lazy_tensor.dtype, device=base_lazy_tensor.device
            )

        if left_interp_indices.shape[:-2] != base_lazy_tensor.batch_shape:
            try:
                base_lazy_tensor = base_lazy_tensor._expand_batch(left_interp_indices.shape[:-2])
            except RuntimeError:
                raise RuntimeError(
                    "interp size ({}) is incompatible with base_lazy_tensor size ({}). ".format(
                        right_interp_indices.size(), base_lazy_tensor.size()
                    )
                )

        super(InterpolatedLazyTensor, self).__init__(
            base_lazy_tensor, left_interp_indices, left_interp_values, right_interp_indices, right_interp_values
        )
        self.base_lazy_tensor = base_lazy_tensor
        self.left_interp_indices = left_interp_indices
        self.left_interp_values = left_interp_values
        self.right_interp_indices = right_interp_indices
        self.right_interp_values = right_interp_values