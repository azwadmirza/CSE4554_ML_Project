        def backward(ctx, grad_output):  # pragma: no cover
            """Implements the backwards pass QNode vector-Jacobian product"""
            # NOTE: This method is definitely tested by the `test_torch.py` test suite,
            # however does not show up in the coverage. This is likely due to
            # subtleties in the torch.autograd.FunctionMeta metaclass, specifically
            # the way in which the backward class is created on the fly

            # evaluate the Jacobian matrix of the QNode
            jacobian = qnode.jacobian(ctx.args, ctx.kwargs)
            jacobian = torch.as_tensor(jacobian, dtype=grad_output.dtype)

            vjp = torch.transpose(grad_output.view(-1, 1), 0, 1) @ jacobian
            vjp = vjp.flatten()

            # restore the nested structure of the input args
            grad_input_list = unflatten_torch(vjp, ctx.saved_tensors)[0]
            grad_input = []

            # match the type and device of the input tensors
            for i, j in zip(grad_input_list, ctx.saved_tensors):
                res = torch.as_tensor(i, dtype=j.dtype)
                if j.is_cuda:  # pragma: no cover
                    cuda_device = j.get_device()
                    res = torch.as_tensor(res, device=cuda_device)
                grad_input.append(res)

            return (None,) + tuple(grad_input)