        def _from_tensor():
            optimizer.param_groups[index][option_key] = dtype(option_tensor.numpy()[0])