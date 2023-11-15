    def _create_option_callback(index, option_key, option_tensor, dtype):
        def _from_tensor():
            optimizer.param_groups[index][option_key] = dtype(option_tensor.numpy()[0])
        return _from_tensor