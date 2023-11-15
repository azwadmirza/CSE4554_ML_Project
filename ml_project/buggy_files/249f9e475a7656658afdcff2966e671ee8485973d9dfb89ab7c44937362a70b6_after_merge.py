def sync_ddp_if_available(
    result: Union[torch.Tensor], group: Optional[Any] = None, reduce_op: Optional[Union[ReduceOp, str]] = None
) -> torch.Tensor:
    """
    Function to reduce a tensor across worker processes during distributed training
    Args:
        result: the value to sync and reduce (typically tensor or number)
        group: the process group to gather results from. Defaults to all processes (world)
        reduce_op: the reduction operation. Defaults to sum.
            Can also be a string of 'avg', 'mean' to calculate the mean during reduction.
    Return:
        reduced value
    """
    if torch.distributed.is_available() and torch.distributed.is_initialized():
        return sync_ddp(result, group=group, reduce_op=reduce_op)
    return result