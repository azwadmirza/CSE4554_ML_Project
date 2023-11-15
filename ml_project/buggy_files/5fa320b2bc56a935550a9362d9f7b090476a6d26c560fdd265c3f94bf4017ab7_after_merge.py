    def create_wrapper(cls, wrapper_type):
        # Note this overrides FrameworkHook.create_wrapper, so it must conform to
        # that classmethod's signature
        if wrapper_type is None or wrapper_type == torch.Tensor:
            return torch.Tensor()
        elif isinstance(wrapper_type, torch.dtype):
            return torch.tensor([], dtype=wrapper_type)
        else:
            raise ValueError(
                "Wrapper type should be None, torch.Tensor, or a torch.dtype like torch.long"
            )