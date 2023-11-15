def convert_to_non_torch_type(stats_dict):
    """Converts values in stats_dict to non-Tensor numpy or python types.

    Args:
        stats_dict (dict): A flat key, value dict, the values of which will be
            converted and returned as a new dict.

    Returns:
        dict: A new dict with the same structure as stats_dict, but with all
            values converted to non-torch Tensor types.
    """
    ret = {}
    for k, v in stats_dict.items():
        if isinstance(v, torch.Tensor):
            ret[k] = v.cpu().item() if len(v.size()) == 0 else v.cpu().numpy()
        else:
            ret[k] = v
    return ret