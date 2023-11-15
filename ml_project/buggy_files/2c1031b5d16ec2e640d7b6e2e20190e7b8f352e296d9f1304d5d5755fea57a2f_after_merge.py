    def backward(ctx, grad_output):  # pragma: no cover
        """Implements the backwards pass QNode vector-Jacobian product"""
        tape = ctx.kwargs["tape"]
        device = ctx.kwargs["device"]

        tape.set_parameters(ctx.all_params_unwrapped, trainable_only=False)
        jacobian = tape.jacobian(device, params=ctx.args, **tape.jacobian_options)
        tape.set_parameters(ctx.all_params, trainable_only=False)

        jacobian = torch.as_tensor(jacobian, dtype=grad_output.dtype).to(grad_output)

        vjp = grad_output.view(1, -1) @ jacobian
        grad_input_list = torch.unbind(vjp.flatten())
        grad_input = []

        # match the type and device of the input tensors
        for i, j in zip(grad_input_list, ctx.saved_tensors):
            res = torch.as_tensor(i, dtype=tape.dtype)
            if j.is_cuda:  # pragma: no cover
                cuda_device = j.get_device()
                res = torch.as_tensor(res, device=cuda_device)
            grad_input.append(res)

        return (None,) + tuple(grad_input)