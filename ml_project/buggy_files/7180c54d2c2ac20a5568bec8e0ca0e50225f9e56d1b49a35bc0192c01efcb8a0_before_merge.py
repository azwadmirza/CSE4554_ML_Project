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
        else:
            if left_interp_indices.size() != left_interp_values.size():
                raise RuntimeError(
                    "Expected left_interp_indices ({}) to have the same size as "
                    "left_interp_values ({})".format(left_interp_indices.size(), left_interp_values.size())
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
        else:
            if left_interp_indices.size() != left_interp_values.size():
                raise RuntimeError(
                    "Expected left_interp_indices ({}) to have the same size as "
                    "left_interp_values ({})".format(left_interp_indices.size(), left_interp_values.size())
                )

        # Make sure that left/right interp tensors have the same batch shape as the base_lazy_tensor
        if left_interp_indices.shape[:-2] != base_lazy_tensor.batch_shape:
            raise RuntimeError(
                "left interp size ({}) is incompatible with base_lazy_tensor size ({}). Make sure the two "
                "have the same number of batch dimensions".format(left_interp_indices.size(), base_lazy_tensor.size())
            )
        if right_interp_indices.shape[:-2] != base_lazy_tensor.batch_shape:
            raise RuntimeError(
                "right interp size ({}) is incompatible with base_lazy_tensor size ({}). Make sure the two "
                "have the same number of batch dimensions".format(right_interp_indices.size(), base_lazy_tensor.size())
            )

        super(InterpolatedLazyTensor, self).__init__(
            base_lazy_tensor, left_interp_indices, left_interp_values, right_interp_indices, right_interp_values
        )
        self.base_lazy_tensor = base_lazy_tensor
        self.left_interp_indices = left_interp_indices
        self.left_interp_values = left_interp_values
        self.right_interp_indices = right_interp_indices
        self.right_interp_values = right_interp_values