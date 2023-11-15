def to_torch(qnode):
    """Function that accepts a :class:`~.QNode`, and returns a PyTorch-compatible QNode.

    Args:
        qnode (~pennylane.qnode.QNode): a PennyLane QNode

    Returns:
        torch.autograd.Function: the QNode as a PyTorch autograd function
    """
    qnode_interface = getattr(qnode, "interface", None)

    if qnode_interface == "torch":
        return qnode

    if qnode_interface is not None:
        qnode = qnode._qnode  # pylint: disable=protected-access

    class _TorchQNode(torch.autograd.Function):
        """The TorchQNode"""

        @staticmethod
        def set_trainable(args):
            """Given input arguments to the TorchQNode, determine which arguments
            are trainable and which aren't.

            Currently, all arguments are assumed to be nondifferentiable by default,
            unless the ``torch.tensor`` attribute ``requires_grad`` is set to True.

            This method calls the underlying :meth:`set_trainable_args` method of the QNode.
            """
            trainable_args = set()

            for idx, arg in enumerate(args):
                if getattr(arg, "requires_grad", False):
                    trainable_args.add(idx)

            qnode.set_trainable_args(trainable_args)

        @staticmethod
        def forward(ctx, input_kwargs, *input_):
            """Implements the forward pass QNode evaluation"""
            # detach all input tensors, convert to NumPy array
            ctx.args = args_to_numpy(input_)
            ctx.kwargs = kwargs_to_numpy(input_kwargs)
            ctx.save_for_backward(*input_)

            # Determine which QNode input tensors require gradients,
            # and thus communicate to the QNode which ones must
            # be wrapped as PennyLane variables.
            _TorchQNode.set_trainable(input_)

            # evaluate the QNode
            res = qnode(*ctx.args, **ctx.kwargs)

            if not isinstance(res, np.ndarray):
                # scalar result, cast to NumPy scalar
                res = np.array(res)

            # if any input tensor uses the GPU, the output should as well
            for i in input_:
                if isinstance(i, torch.Tensor):
                    if i.is_cuda:  # pragma: no cover
                        cuda_device = i.get_device()
                        return torch.as_tensor(torch.from_numpy(res), device=cuda_device)

            return torch.from_numpy(res)

        @staticmethod
        @once_differentiable
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

    class TorchQNode(partial):
        """Torch QNode"""

        # pylint: disable=too-few-public-methods

        # Here, we are making use of functools.partial to dynamically add
        # methods and attributes to the custom gradient method defined below.
        # This allows us to provide more useful __str__ and __repr__ methods
        # for the decorated function (so it would still look like a QNode to end-users),
        # as well as making QNode attributes and methods available.

        @property
        def interface(self):
            """String representing the QNode interface"""
            return "torch"

        def __str__(self):
            """String representation"""
            detail = "<QNode: device='{}', func={}, wires={}, interface={}>"
            return detail.format(
                qnode.device.short_name, qnode.func.__name__, qnode.num_wires, self.interface
            )

        def __repr__(self):
            """REPL representation"""
            return self.__str__()

        # Bind QNode methods
        print_applied = qnode.print_applied
        jacobian = qnode.jacobian
        metric_tensor = qnode.metric_tensor
        draw = qnode.draw
        func = qnode.func
        set_trainable_args = qnode.set_trainable_args
        get_trainable_args = qnode.get_trainable_args
        _qnode = qnode

        # Bind QNode attributes. Note that attributes must be
        # bound as properties; by making use of closure, we ensure
        # that updates to the wrapped QNode attributes are reflected
        # by the wrapper class.
        arg_vars = property(lambda self: qnode.arg_vars)
        num_variables = property(lambda self: qnode.num_variables)
        par_to_grad_method = property(lambda self: qnode.par_to_grad_method)

    @TorchQNode
    def custom_apply(*args, **kwargs):
        """Custom apply wrapper, to allow passing kwargs to the TorchQNode"""

        # get default kwargs that weren't passed
        keyword_sig = _get_default_args(qnode.func)
        keyword_defaults = {k: v[1] for k, v in keyword_sig.items()}
        # keyword_positions = {v[0]: k for k, v in keyword_sig.items()}

        # create a keyword_values dict, that contains defaults
        # and any user-passed kwargs
        keyword_values = {}
        keyword_values.update(keyword_defaults)
        keyword_values.update(kwargs)

        # sort keyword values into a list of args, using their position
        # [keyword_values[k] for k in sorted(keyword_positions, key=keyword_positions.get)]

        return _TorchQNode.apply(keyword_values, *args)

    return custom_apply