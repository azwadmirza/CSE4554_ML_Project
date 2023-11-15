    def _worker(i, module, input, kwargs, device=None):
        torch.set_grad_enabled(grad_enabled)
        fx_called: str = ''
        if device is None:
            device = get_a_var(input).get_device()
        try:
            with torch.cuda.device(device):
                # this also avoids accidental slicing of `input` if it is a Tensor
                if not isinstance(input, (list, tuple)):
                    input = (input,)

                module = module.to(device)

                # ---------------
                # CHANGE
                if module.training:
                    output = module.training_step(*input, **kwargs)
                    fx_called = 'training_step'
                elif module.testing:
                    output = module.test_step(*input, **kwargs)
                    fx_called = 'test_step'
                else:
                    output = module.validation_step(*input, **kwargs)
                    fx_called = 'validation_step'

                if output is None:
                    warn_missing_output(fx_called)

                if output is not None and (module.use_dp or module.use_ddp2):
                    auto_squeeze_dim_zeros(output)
                # ---------------

            with lock:
                results[i] = output
        except Exception as ex:
            with lock:
                results[i] = ex