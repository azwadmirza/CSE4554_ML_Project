    def create_wrapper(cls, wrapper_type):
        # Note this overrides FrameworkHook.create_wrapper, so it must conform to
        # that classmethod's signature
        assert (
            wrapper_type is None or wrapper_type == torch.Tensor
        ), "TorchHook only uses torch.Tensor wrappers"

        return torch.Tensor()