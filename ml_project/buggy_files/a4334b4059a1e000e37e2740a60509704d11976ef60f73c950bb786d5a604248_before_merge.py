def allreduce(tensor, average=None, device_dense='', device_sparse='',
              compression=Compression.none, op=None):
    """Perform an allreduce on a tf.Tensor or tf.IndexedSlices.

    This function performs a bandwidth-optimal ring allreduce on the input
    tensor. If the input is an tf.IndexedSlices, the function instead does an
    allgather on the values and the indices, effectively doing an allreduce on
    the represented tensor.

    Arguments:
        tensor: tf.Tensor, tf.Variable, or tf.IndexedSlices to reduce.
                The shape of the input must be identical across all ranks.
        average: DEPRECATED, please use op instead.
        device_dense: Device to be used for dense tensors. Uses GPU by default
                      if Horovod was built with HOROVOD_GPU_ALLREDUCE.
        device_sparse: Device to be used for sparse tensors. Uses GPU by default
                       if Horovod was built with HOROVOD_GPU_ALLGATHER.
        compression: Compression algorithm used to reduce the amount of data
                     sent and received by each worker node.  Defaults to not
                     using compression.
        op: The reduction operation to combine tensors across different ranks.
            Defaults to Average if None is given.

    Returns:
        A tensor of the same shape and type as `tensor`, summed across all
        processes.
    """
    op = handle_average_backwards_compatibility(op, average)
    # Averaging happens in framework code, so translate that to Sum for the actual call
    true_op = Sum if op == Average else op

    if isinstance(tensor, tf.IndexedSlices):
        # TODO: Need to fix this to actuall call Adasum
        if op == Adasum:
            raise NotImplementedError("The Adasum reduction does not currently support "
                "sparse tensors. As a workaround please pass sparse_as_dense=True to "
                "DistributedOptimizer")
        with tf.device(device_sparse):
            # For IndexedSlices, do two allgathers instead of an allreduce.
            horovod_size = tf.cast(size(), tensor.values.dtype)
            values = allgather(tensor.values)
            indices = allgather(tensor.indices)

            # To make this operation into an average, divide allgathered values by
            # the Horovod size.
            new_values = (values / horovod_size) if op == Average else values
        return tf.IndexedSlices(new_values, indices,
                                dense_shape=tensor.dense_shape)
    else:
        with tf.device(device_dense):
            horovod_size = tf.cast(size(), dtype=tensor.dtype)
            tensor_compressed, ctx = compression.compress(tensor)
            summed_tensor_compressed = _allreduce(tensor_compressed, op=true_op)
            summed_tensor = compression.decompress(summed_tensor_compressed, ctx)
            if op == Adasum:
                if ('CPU' not in tensor.device and has_gpu):
                    if nccl_built():
                        if not is_homogeneous:
                            raise NotImplementedError('Running GPU Adasum on heterogeneous cluster is not supported yet.')
                        elif not check_num_rank_power_of_2(int(size() / local_size())):
                            raise NotImplementedError('Running GPU Adasum with non-power of 2 nodes is not supported yet.')
                        horovod_local_size = tf.cast(local_size(), dtype=tensor.dtype)
                        new_tensor = summed_tensor / horovod_local_size
                    else:
                        warnings.warn("Adasum reduction does not currently support "
                            "GPU reduction using MPI. Tensors are copied to CPU memory instead."
                            "To use Adasum for GPU reduction, please compile Horovod with HOROVOD_GPU_ALLREDUCE=NCCL.")
                        new_tensor = summed_tensor
                else:
                    if not check_num_rank_power_of_2(size()):
                        raise NotImplementedError('Running Adasum with non-power of 2 ranks is not supported yet.')
                    new_tensor = summed_tensor
            else:
                new_tensor = (summed_tensor / horovod_size) if op == Average else summed_tensor
        return new_tensor