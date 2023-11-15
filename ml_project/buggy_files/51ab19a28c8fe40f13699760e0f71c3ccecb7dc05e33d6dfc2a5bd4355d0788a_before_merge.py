def _allreduce_async(tensor, output, name, op):
    if tensor.dtype == torch.float16 and not _fp16_supported:
        raise NotImplementedError(
            'float16 allreduce is not supported for PyTorch version {} < 1.0.0'
            .format(torch.__version__))

    # Set the divisor for reduced gradients to average when necessary
    if op == Average:
        divisor = size()
    elif (op == Adasum):
        if (tensor.device.type != 'cpu' and _has_gpu):
            if nccl_built():
                if not is_homogeneous():
                    raise NotImplementedError('Running GPU Adasum on heterogeneous cluster is not supported yet.')
                elif not num_rank_is_power_2(int(size() / local_size())):
                    raise NotImplementedError('Running GPU Adasum with non-power of 2 nodes is not supported yet.')
                divisor = local_size()
            else:
                warnings.warn("Adasum reduction does not currently support "
                    "GPU reduction using MPI. Tensors are copied to CPU memory instead."
                    "To use Adasum for GPU reduction, please compile Horovod with HOROVOD_GPU_ALLREDUCE=NCCL.")
                divisor = 1
        else:
            if not num_rank_is_power_2(size()):
                raise NotImplementedError('Running Adasum with non-power of 2 ranks is not supported yet.')
            divisor = 1
    else:
        divisor = 1
    # Averaging happens in framework code, so translate that to Sum for the actual call
    true_op = Sum if op == Average else op

    function = _check_function(_allreduce_function_factory, tensor)
    handle = getattr(mpi_lib, function)(tensor, output, divisor,
                                        name.encode() if name is not None else _NULL, true_op)
    _handle_map[handle] = (tensor, output)
    return handle