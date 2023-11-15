    def __call__(self, tensor: torch.Tensor, parameter_name: str, **kwargs) -> None:  # type: ignore
        # Select the new parameter name if it's being overridden
        if parameter_name in self.parameter_name_overrides:
            parameter_name = self.parameter_name_overrides[parameter_name]

        # If the size of the source and destination tensors are not the
        # same, then we need to raise an error
        source_weights = self.weights[parameter_name]
        if tensor.data.size() != source_weights.size():
            raise ConfigurationError(
                "Incompatible sizes found for parameter %s. "
                "Found %s and %s" % (parameter_name, tensor.data.size(), source_weights.size())
            )

        # Copy the parameters from the source to the destination
        tensor.data.copy_(source_weights.data)