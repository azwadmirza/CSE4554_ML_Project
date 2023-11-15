def auto_squeeze_dim_zeros(output):
    """
    In DP or DDP2 we need to unsqueeze dim 0
    :param output:
    :return:
    """
    for k, v in output.items():
        if not isinstance(v, torch.Tensor):
            continue

        is_scalar = v.dim() == 0
        if is_scalar:
            output[k] = output[k].unsqueeze(0)