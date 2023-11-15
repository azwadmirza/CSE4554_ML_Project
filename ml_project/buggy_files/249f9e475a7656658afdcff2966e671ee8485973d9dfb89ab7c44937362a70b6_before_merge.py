def sync_ddp_if_available(
    result: Union[torch.Tensor], group: Optional[Any] = None, reduce_op: Optional[Union[ReduceOp, str]] = None
) -> torch.Tensor:
    """
    Function to reduce the tensors from several ddp processes to one master process

    Args:
        result: the value to sync and reduce (typically tensor or number)
        group: the process group to gather results from. Defaults to all processes (world)
        reduce_op: the reduction operation. Defaults to sum.
            Can also be a string of 'avg', 'mean' to calculate the mean during reduction.

    Return:
        reduced value
    """

    if torch.distributed.is_available() and torch.distributed.is_initialized():
        divide_by_world_size = False

        if group is None:
            group = torch.distributed.group.WORLD

        if reduce_op is None:
            reduce_op = torch.distributed.ReduceOp.SUM
        elif isinstance(reduce_op, str) and reduce_op in ("avg", "mean"):
            reduce_op = torch.distributed.ReduceOp.SUM
            divide_by_world_size = True

        # sync all processes before reduction
        torch.distributed.barrier(group=group)
        torch.distributed.all_reduce(result, op=reduce_op, group=group, async_op=False)

        if divide_by_world_size:
            result = result / torch.distributed.get_world_size(group)

    return result