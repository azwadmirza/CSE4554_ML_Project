def allgather(tensor, name=None, priority=0):
    """
    A function that concatenates the input tensor with the same input tensor on
    all other Horovod processes. The input tensor is not modified.

    The concatenation is done on the first dimension, so the input tensors on
    the different processes must have the same rank and shape, except for the
    first dimension, which is allowed to be different.

    This acts as a thin wrapper around an autograd function.  If your input
    tensor requires gradients, then callings this function will allow gradients
    to be computed and backpropagated.

    Arguments:
        tensor: A tensor to allgather.
        name: A name of the allgather operation.
        priority: The priority of this operation. Higher priority operations
                  are likely to be executed before other operations.

    Returns:
        A tensor of the same type as `tensor`, concatenated on dimension zero
        across all processes. The shape is identical to the input shape, except
        for the first dimension, which may be greater and is the sum of all
        first dimensions of the tensors in different Horovod processes.
    """
    assert(isinstance(tensor, mx.nd.NDArray))
    output = mx.nd.zeros(shape=tensor.shape, ctx=tensor.context,
                         dtype=tensor.dtype)
    c_in = tensor.handle
    c_out = output.handle
    if isinstance(name, string_types):
        check_call(MPI_MXNET_LIB_CTYPES.horovod_mxnet_allgather_async(
            c_in, c_out, c_str(name), ctypes.c_int(priority)))
    else:
        check_call(MPI_MXNET_LIB_CTYPES.horovod_mxnet_allgather_async(
            c_in, c_out, name, ctypes.c_int(priority)))
    return output